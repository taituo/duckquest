#!/usr/bin/env bash
# Steam Deck helper for TrackQuest development.
#
# Two ways to run:
#   A) Dev mode (recommended while coding): server runs on the Mac,
#      the Deck is just the TV screen showing http://<mac-ip>:8080
#   B) Deck mode: code is copied to the Deck and the server runs there.
#
# Usage:  scripts/deck.sh <command> [args]
#   check              ssh works, python/browser/display found on the Deck
#   open [URL]         open URL fullscreen on the Deck's screen (default: Mac dev server)
#   close              close the browser on the Deck
#   deploy             copy duckquest/ to the Deck (~/trackquest/duckquest)
#   serve              start server.py on the Deck in the background
#   stop               stop server.py on the Deck
#   logs               show the Deck server log
#   pad [HOST]         run the gamepad bridge on the Deck (default HOST: the Mac); `pad stop` stops it
#   shot [FILE]        screenshot the Deck desktop (both screens) to FILE (default /tmp/deck.png)
#   ip                 print Mac and Deck LAN addresses
#
# Env: DECK_HOST (default "deck", your ssh alias), PORT (default 8080)
set -euo pipefail

DECK_HOST="${DECK_HOST:-deck}"
PORT="${PORT:-8080}"
REMOTE_DIR="trackquest"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Environment so GUI apps started over ssh appear on the Deck's screen (X11 or Wayland).
GUI_ENV='export DISPLAY=:0; export XAUTHORITY=$(ls /run/user/$(id -u)/xauth_* 2>/dev/null | head -1); export XDG_RUNTIME_DIR=/run/user/$(id -u);
[ -S "$XDG_RUNTIME_DIR/wayland-0" ] && export WAYLAND_DISPLAY=wayland-0;
export DBUS_SESSION_BUS_ADDRESS=unix:path=$XDG_RUNTIME_DIR/bus;'

mac_ip() {
  ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}'
}

deck() { ssh -o ConnectTimeout=5 "$DECK_HOST" "$@"; }

# Pick a browser on the Deck: Flatpak Chrome / Chromium / Firefox, or a native one.
BROWSER_PICK='
if flatpak info com.google.Chrome >/dev/null 2>&1; then B="flatpak run com.google.Chrome --kiosk --noerrdialogs --autoplay-policy=no-user-gesture-required";
elif flatpak info org.chromium.Chromium >/dev/null 2>&1; then B="flatpak run org.chromium.Chromium --kiosk --noerrdialogs --autoplay-policy=no-user-gesture-required";
elif flatpak info org.mozilla.firefox >/dev/null 2>&1; then B="flatpak run org.mozilla.firefox --new-window";
elif command -v firefox >/dev/null; then B="firefox --new-window";
else B=""; fi'

cmd="${1:-help}"; shift || true
case "$cmd" in
  check)
    echo "== ssh $DECK_HOST"
    deck "echo ok: \$(hostname), user \$(whoami); python3 --version;
      $GUI_ENV
      echo DISPLAY=\$DISPLAY WAYLAND_DISPLAY=\${WAYLAND_DISPLAY:-none};
      echo session: \${XDG_SESSION_TYPE:-?}; loginctl list-sessions --no-legend 2>/dev/null | head -3;
      $BROWSER_PICK
      echo browser: \${B:-NONE FOUND - install Chrome or Firefox from Discover};
      ip -4 -o addr show scope global | awk '{print \"deck ip:\", \$4}'"
    echo "mac ip: $(mac_ip)"
    ;;
  open)
    URL="${1:-http://$(mac_ip):$PORT/}"
    echo "Opening $URL on the Deck"
    # TV = the extended-desktop output right of the Deck's own screen; KDE's Meta+Shift+Right sends the window there, then F11.
    deck "$GUI_ENV $BROWSER_PICK
      [ -z \"\$B\" ] && { echo 'No browser found on the Deck'; exit 1; }
      for a in org.mozilla.firefox com.google.Chrome org.chromium.Chromium; do flatpak kill \$a 2>/dev/null; done; pkill -x firefox 2>/dev/null || true; sleep 1
      TV=\$(xrandr | awk '/ connected/ && !/primary/ {print \$3}' | head -1)   # e.g. 1920x1080+1280+0
      TVX=\$(echo \"\$TV\" | cut -d+ -f2); TVY=\$(echo \"\$TV\" | cut -d+ -f3)
      nohup \$B '$URL' >/tmp/trackquest-browser.log 2>&1 &
      WID=''; for i in \$(seq 1 40); do WID=\$(xdotool search --onlyvisible --class -- 'firefox|chrom' 2>/dev/null | tail -1); [ -n \"\$WID\" ] && break; sleep 0.5; done
      [ -z \"\$WID\" ] && { echo 'browser window did not appear'; tail -5 /tmp/trackquest-browser.log; exit 1; }
      sleep 1; xdotool windowactivate \$WID; sleep 0.5; xdotool key super+shift+Right; sleep 1.5; xdotool key F11
      echo started on TV: \$B"
    ;;
  close)
    deck "for a in org.mozilla.firefox com.google.Chrome org.chromium.Chromium; do flatpak kill \$a 2>/dev/null; done; pkill -x firefox; echo closed || echo 'nothing to close'"
    ;;
  deploy)
    deck "mkdir -p ~/$REMOTE_DIR"
    rsync -az --delete --exclude '__pycache__' --exclude '*.pem' "$ROOT/duckquest/" "$DECK_HOST:$REMOTE_DIR/duckquest/"
    echo "Copied duckquest/ to $DECK_HOST:~/$REMOTE_DIR/duckquest"
    ;;
  serve)
    deck "cd ~/$REMOTE_DIR/duckquest && pkill -f 'python3 server.py' 2>/dev/null; sleep 0.5;
      nohup python3 server.py --port $PORT > ~/$REMOTE_DIR/server.log 2>&1 & sleep 2; cat ~/$REMOTE_DIR/server.log"
    ;;
  stop)
    deck "pkill -f 'python3 server.py' && echo stopped || echo 'not running'"
    ;;
  shot)
    OUT="${1:-/tmp/deck.png}"
    deck "$GUI_ENV xset dpms force on; spectacle -b -n -f -o /tmp/deck-shot.png" >/dev/null 2>&1
    scp -q "$DECK_HOST:/tmp/deck-shot.png" "$OUT" && echo "Saved $OUT"
    ;;
  pad)
    if [ "${1:-}" = "stop" ]; then deck "systemctl --user stop trackquest-pad && echo stopped || echo 'not running'"; exit 0; fi
    deck "mkdir -p ~/$REMOTE_DIR"
    scp -q "$ROOT/duckquest/padbridge.py" "$DECK_HOST:$REMOTE_DIR/padbridge.py"
    # transient user service: survives the ssh session, restarts on failure
    deck "systemctl --user stop trackquest-pad 2>/dev/null; systemctl --user reset-failed trackquest-pad 2>/dev/null;
      systemd-run --user -q -u trackquest-pad -p Restart=always -p RestartSec=2 python3 -u /home/deck/$REMOTE_DIR/padbridge.py --host ${1:-$(mac_ip)} --port $PORT
      sleep 1.5; systemctl --user is-active trackquest-pad; journalctl --user -u trackquest-pad -n 3 --no-pager -o cat"
    ;;
  logs)
    deck "tail -n 50 ~/$REMOTE_DIR/server.log"
    ;;
  ip)
    echo "mac:  $(mac_ip)"
    deck "ip -4 -o addr show scope global | awk '{print \"deck:\", \$4}'"
    ;;
  *)
    sed -n '2,20p' "$0"
    ;;
esac
