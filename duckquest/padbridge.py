#!/usr/bin/env python3
"""Gamepad bridge for DuckQuest - Python 3 standard library only (Linux).

Reads a Linux joystick device (/dev/input/js0, e.g. the Steam Deck's built-in
controls) and sends stick/button state to the DuckQuest server as role "pad".
Used when the browser cannot see the gamepad (Flatpak, Steam Input desktop layout).

  python3 padbridge.py --host <server-ip> --port 8080 [--dev /dev/input/js0]
"""
import argparse, base64, json, os, socket, struct, time

# Xbox-style js layout -> "standard" gamepad layout the game expects
BTN = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 8, 7: 9}   # A B X Y LB RB Back Start
AX = {0: 0, 1: 1, 3: 2, 4: 3}                              # LX LY RX RY
LT_AX, RT_AX = 2, 5
HAT_X, HAT_Y = 6, 7                                       # D-pad hat -> standard buttons 14/15 and 12/13
BTN.update({9: 10, 10: 11})                                # L3 R3


def ws_connect(host, port):
    s = socket.create_connection((host, port), timeout=5)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall((f"GET /ws?role=pad HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        d = s.recv(1024)
        if not d:
            raise ConnectionError("handshake failed")
        buf += d
    if b" 101 " not in buf.split(b"\r\n", 1)[0]:
        raise ConnectionError("server refused websocket")
    s.settimeout(None)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return s


def ws_send(s, text):
    data = text.encode()
    n = len(data)
    head = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n))
    mask = os.urandom(4)
    s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--dev", default="/dev/input/js0")
    a = ap.parse_args()
    axes, btns = [0.0] * 4, set()
    lt = rt = 0.0
    hat = [0, 0]
    while True:
        try:
            sock = ws_connect(a.host, a.port)
            print(f"pad bridge connected to {a.host}:{a.port}, reading {a.dev}", flush=True)
            dev = open(a.dev, "rb", buffering=0)
            last = 0.0
            dirty = True
            import select
            while True:
                r, _, _ = select.select([dev], [], [], 0.25)
                if r:
                    _, v, ty, i = struct.unpack("IhBB", dev.read(8))
                    if ty & 0x01 and i in BTN:                      # button
                        (btns.add if v else btns.discard)(BTN[i]); dirty = True
                    elif ty & 0x02:                                  # axis
                        if i in AX: axes[AX[i]] = round(v / 32767, 3)
                        elif i == LT_AX: lt = (v + 32767) / 65534
                        elif i == RT_AX: rt = (v + 32767) / 65534
                        elif i == HAT_X: hat[0] = -1 if v < -16000 else 1 if v > 16000 else 0
                        elif i == HAT_Y: hat[1] = -1 if v < -16000 else 1 if v > 16000 else 0
                        dirty = True
                now = time.time()
                if dirty and now - last > 0.012 or now - last > 1.0:
                    b = set(btns)
                    if lt > 0.5: b.add(6)
                    if rt > 0.5: b.add(7)
                    if hat[1] < 0: b.add(12)
                    if hat[1] > 0: b.add(13)
                    if hat[0] < 0: b.add(14)
                    if hat[0] > 0: b.add(15)
                    ws_send(sock, json.dumps({"type": "pad", "axes": axes, "btn": sorted(b)}))
                    last, dirty = now, False
        except (OSError, ConnectionError) as e:
            print("bridge:", e, "- retrying in 2s", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
