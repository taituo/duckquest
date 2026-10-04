#!/usr/bin/env bash
# Meta Quest helper over adb (needs Developer Mode + USB debugging allowed once).
#
# Usage:  scripts/quest.sh <command> [args]
#   check              show whether adb sees the Quest, battery and wake state
#   wake               wake the headset and keep it awake (fake "worn" proximity)
#   shot [FILE]        grab one frame of what the Quest displays (default /tmp/quest-frame.png).
#                      The picture is both eyes side by side; it is upside down if the headset lies on its back.
#   mirror             live mirror window (scrcpy)
#   open [URL]         open a URL in the Quest browser (default: the tracker page of the Mac server)
set -euo pipefail
cmd="${1:-help}"; shift || true
mac_ip() { ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1; }
case "$cmd" in
  check)
    adb devices -l
    adb shell dumpsys battery | grep -E "level|status" | head -2
    adb shell dumpsys power | grep -m1 mWakefulness=
    ;;
  wake)
    adb shell am broadcast -a com.oculus.vrpowermanager.prox_close >/dev/null
    adb shell input keyevent KEYCODE_WAKEUP
    adb shell dumpsys power | grep -m1 mWakefulness=
    ;;
  shot)
    OUT="${1:-/tmp/quest-frame.png}"; TMP="$(mktemp -t quest).mkv"
    scrcpy --no-audio --no-playback --no-window --record="$TMP" >/dev/null 2>&1 &
    PID=$!; sleep 5; kill "$PID" 2>/dev/null || true; sleep 1
    ffmpeg -loglevel error -y -sseof -2 -i "$TMP" -frames:v 1 "$OUT" && rm -f "$TMP" && echo "Saved $OUT"
    ;;
  mirror)
    exec scrcpy --no-audio --window-title "Quest 3"
    ;;
  open)
    URL="${1:-https://$(mac_ip):8443/quest.html}"
    adb shell am start -a android.intent.action.VIEW -d "$URL" >/dev/null && echo "Opened $URL on the Quest"
    ;;
  *)
    sed -n '2,13p' "$0"
    ;;
esac
