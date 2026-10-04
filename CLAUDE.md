# TrackQuest — notes for Claude Code

Meta Quest 3 used as a stationary controller tracker for TV games. See `README.md` for the idea list and `docs/` for background.

## Hardware on this LAN

- **Mac M1**: development machine, runs Claude Code.
- **Steam Deck** in Desktop Mode, connected to a small TV (likely mirrored display). Reachable as `ssh deck` (key auth). Never read, print or use credential files on the Deck; nothing here needs sudo.
- **Meta Quest 3**: joins later, same Wi-Fi.

Longer project notes (lessons, runbook, checklists) live in `reports/` when present.

## Dev loop (recommended)

Run the server **on the Mac**, use the Deck only as the TV screen:

```bash
python3 duckquest/server.py          # on the Mac, prints the Quest URL
scripts/deck.sh check                # verify ssh, display, browser on the Deck
scripts/deck.sh open                 # Deck shows http://<mac-ip>:8080 fullscreen
```

Edit files on the Mac → `scripts/deck.sh open` again (or press F5 on the Deck) to reload.

The Quest opens `https://<mac-ip>:8443/quest.html` (accept the cert warning once).

macOS will ask to allow incoming connections for Python the first time; allow it, or the Deck and Quest can't connect.

## Gamepad on the Deck

The Deck's own buttons reach the page as a virtual Xbox 360 pad only if the Flatpak Firefox may see input devices: `ssh deck 'flatpak override --user --device=all org.mozilla.firefox'` (done once, no sudo), then `scripts/deck.sh open`. Press any button once so the browser exposes the pad.

Sound after a reload needs a user gesture unless Firefox autoplay is allowed: `media.autoplay.default=0` is set in the Flatpak profile's `user.js` (`~/.var/app/org.mozilla.firefox/config/mozilla/firefox/*.default-release/`). The Deck's own gamepad input goes through `scripts/deck.sh pad` (padbridge.py as a systemd user service).

## Deck mode (standalone, no Mac)

```bash
scripts/deck.sh deploy && scripts/deck.sh serve && scripts/deck.sh open http://localhost:8080/
```

## Bring-up order

1. `scripts/deck.sh check`: ssh ok, python3 found, a browser found, display env works.
   - If no browser: install Chrome or Firefox from Discover on the Deck (Flatpak).
   - If the window doesn't appear on screen: check `check` output for X11 vs Wayland and adjust `GUI_ENV` in `scripts/deck.sh`.
2. Without the Quest: start the Mac server, `open` on the Deck, test with the Deck's trackpad/mouse (mouse = player 3). Sound needs one click/keypress on the Deck.
3. With the Quest: open the tracker page, Start tracking, tape the proximity sensor, place it, calibrate (A/X or C = aim mode).
4. Debug: press D on the game screen for pose age and raw positions.

## Seeing the Quest's view on the Mac (optional)

- **Casting**: Quest quick settings → Cast → to the phone app or a browser at the Meta casting page.
- **scrcpy** (needs Quest developer mode): `brew install scrcpy android-platform-tools`, connect the Quest by USB, `scrcpy --crop 1730:974:1934:450` (crop values vary by model; plain `scrcpy` first).

## Conventions

- `duckquest/server.py` uses only the Python standard library. Keep it that way.
- Games are single-file HTML (no build step). New games go in their own folder next to `duckquest/`.
- Don't commit `cert.pem` / `key.pem` (ignored).
