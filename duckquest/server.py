#!/usr/bin/env python3
"""
DuckQuest relay server  -  Python 3 standard library only (no pip installs).

  * Serves the game + tracker pages.
  * Relays controller poses:  Quest tracker page  ->  game page(s)
    and haptic requests:       game page          ->  Quest.

Runs two ports:
  http://<deck-ip>:8080   -> open game.html here on the Steam Deck / PC (http://localhost:8080)
  https://<deck-ip>:8443  -> open quest.html here in the Quest Browser
                             (WebXR needs HTTPS; a self-signed cert is generated automatically)

Usage:  python3 server.py  [--port 8080] [--https-port 8443] [--no-https]
"""
import argparse
import base64
import hashlib
import http.server
import json
import os
import shutil
import socket
import ssl
import struct
import time
import subprocess
import sys
import threading
from urllib.parse import urlparse, parse_qs

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
ROOT = os.path.dirname(os.path.abspath(__file__))

clients = {"quest": set(), "game": set(), "pad": set()}
clients_lock = threading.Lock()


class WSConn:
    """One WebSocket connection (minimal RFC 6455: text, ping, close)."""

    def __init__(self, handler, role):
        self.h = handler
        self.role = role
        self.lock = threading.Lock()

    def _send(self, opcode, data):
        n = len(data)
        b0 = 0x80 | opcode
        if n < 126:
            hdr = struct.pack("!BB", b0, n)
        elif n < 65536:
            hdr = struct.pack("!BBH", b0, 126, n)
        else:
            hdr = struct.pack("!BBQ", b0, 127, n)
        with self.lock:
            try:
                self.h.wfile.write(hdr + data)
                self.h.wfile.flush()
            except Exception:
                pass

    def send_text(self, text):
        self._send(0x1, text.encode("utf-8"))

    def recv(self):
        r = self.h.rfile
        head = r.read(2)
        if len(head) < 2:
            return None
        opcode = head[0] & 0x0F
        masked = head[1] & 0x80
        n = head[1] & 0x7F
        if n == 126:
            n = struct.unpack("!H", r.read(2))[0]
        elif n == 127:
            n = struct.unpack("!Q", r.read(8))[0]
        mask = r.read(4) if masked else b"\x00\x00\x00\x00"
        payload = bytearray(r.read(n))
        if len(payload) < n:
            return None
        if masked:
            for i in range(n):
                payload[i] ^= mask[i & 3]
        return opcode, bytes(payload)


def broadcast_status():
    with clients_lock:
        msg = json.dumps({"type": "status",
                          "quests": len(clients["quest"]),
                          "games": len(clients["game"])})
        everyone = list(clients["quest"]) + list(clients["game"])
    for c in everyone:
        c.send_text(msg)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        # /duel/... and /boxing/... are served from sibling folders (other games live next to duckquest/)
        up = urlparse(path).path
        for game in ("duel", "boxing", "reach"):
            if up.startswith("/" + game + "/"):
                saved = self.directory
                self.directory = os.path.join(os.path.dirname(ROOT), game)
                try:
                    return super().translate_path(up[len(game) + 1:])
                finally:
                    self.directory = saved
        return super().translate_path(path)

    def log_message(self, fmt, *args):  # keep the console quiet
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/ws" and self.headers.get("Upgrade", "").lower() == "websocket":
            role = parse_qs(u.query).get("role", ["game"])[0]
            return self.handle_ws(role if role in clients else "game")
        if u.path == "/calib":                      # saved calibration (written by the game)
            try:
                data = open(os.path.join(ROOT, "calib.json"), "rb").read()
            except OSError:
                self.send_error(404); return
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        if u.path == "/":
            self.path = "/game.html"
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/calib":
            self.send_error(404); return
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n <= 0 or n > 65536:
            self.send_error(400); return
        try:
            body = self.rfile.read(n); json.loads(body)
        except Exception:
            self.send_error(400); return
        path = os.path.join(ROOT, "calib.json")
        try:
            if os.path.exists(path):
                if open(path, "rb").read() != body:                          # keep every different previous version
                    bdir = os.path.join(ROOT, "calib-backups"); os.makedirs(bdir, exist_ok=True)
                    shutil.copy2(path, os.path.join(bdir, time.strftime("calib-%Y%m%d-%H%M%S.json")))
                    for old_f in sorted(os.listdir(bdir))[:-30]:
                        os.remove(os.path.join(bdir, old_f))
                os.replace(path, os.path.join(ROOT, "calib.prev.json"))
            with open(path, "wb") as f:
                f.write(body)
        except OSError:
            self.send_error(500); return
        self.send_response(204); self.end_headers()

    def handle_ws(self, role):
        key = self.headers.get("Sec-WebSocket-Key", "")
        accept = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
        # Raw HTTP/1.1 response: Firefox rejects the HTTP/1.0 status line the base handler would send.
        self.wfile.write(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                          "Connection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n" % accept).encode())
        self.wfile.flush()
        try:
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception:
            pass

        conn = WSConn(self, role)
        with clients_lock:
            clients[role].add(conn)
        print(f"[+] {role} connected from {self.client_address[0]}")
        broadcast_status()
        other = "game" if role in ("quest", "pad") else "quest"
        try:
            while True:
                frame = conn.recv()
                if frame is None:
                    break
                opcode, payload = frame
                if opcode == 0x8:      # close
                    break
                if opcode == 0x9:      # ping -> pong
                    conn._send(0xA, payload)
                    continue
                if opcode != 0x1:      # only relay text
                    continue
                text = payload.decode("utf-8", "replace")
                if role == "quest" and text[:24].replace(" ", "").startswith('{"type":"log"'):   # debug log from the Quest page: print, don't relay
                    try:
                        m = json.loads(text)
                        print(f"[quest {m.get('level', 'log')}] {m.get('msg', '')}", flush=True)
                    except Exception:
                        pass
                    continue
                with clients_lock:
                    targets = list(clients[other])
                for t in targets:
                    t.send_text(text)
        except Exception:
            pass
        finally:
            with clients_lock:
                clients[role].discard(conn)
            print(f"[-] {role} disconnected")
            broadcast_status()
            self.close_connection = True


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def ensure_cert():
    cert, key = os.path.join(ROOT, "cert.pem"), os.path.join(ROOT, "key.pem")
    if os.path.exists(cert) and os.path.exists(key):
        return cert, key
    if not shutil.which("openssl"):
        return None
    print("Generating self-signed certificate (one time)...")
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                    "-keyout", key, "-out", cert, "-days", "3650",
                    "-subj", "/CN=duckquest"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return cert, key


def main():
    ap = argparse.ArgumentParser(description="DuckQuest relay server")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--https-port", type=int, default=8443)
    ap.add_argument("--no-https", action="store_true")
    args = ap.parse_args()

    http.server.ThreadingHTTPServer.daemon_threads = True
    ip = lan_ip()

    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    print("\n=== DuckQuest server running ===")
    print(f"  Game  (Steam Deck browser):  http://localhost:{args.port}")

    if not args.no_https:
        pair = ensure_cert()
        if pair:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(*pair)
            httpsd = http.server.ThreadingHTTPServer(("0.0.0.0", args.https_port), Handler)
            httpsd.socket = ctx.wrap_socket(httpsd.socket, server_side=True)
            threading.Thread(target=httpsd.serve_forever, daemon=True).start()
            print(f"  Tracker (Quest Browser):     https://{ip}:{args.https_port}/quest.html")
            print("     -> accept the certificate warning once (Advanced / Proceed)")
        else:
            print("  ! openssl not found, HTTPS disabled. See README for the Quest flag workaround.")
            print(f"  Tracker (Quest Browser):     http://{ip}:{args.port}/quest.html")
    print("\nCtrl+C to stop.\n")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("bye")
        sys.exit(0)


if __name__ == "__main__":
    main()
