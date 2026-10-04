# Connecting devices and sharing

## Connecting

- Only **Wi-Fi** is needed. The Quest and the computer must be on the **same network**.
- The computer runs `server.py` (Python 3, standard library only) and shows the game in a browser.
- The Quest opens the tracker page from the computer's address and streams controller data to it.
- Any computer works: Steam Deck, Windows PC (allow Python through the firewall), Mac, Linux, mini PC.

Tips:
- Use **5 GHz Wi-Fi**, router fairly close, for low and steady lag.
- Guest networks and some mesh setups block devices from talking to each other.
- Optional: a USB cable from the Quest to the computer gives the lowest lag and avoids the certificate warning.

## Why a web page, not an app (for now)

- No developer mode or sideloading. Just open a link.
- Change code on the computer and reload on the Quest.
- Same tracking quality as an app.

WebXR needs HTTPS, so the server makes a self-signed certificate and serves the tracker on port 8443. If the Quest Browser offers no "Proceed" on the warning, use `chrome://flags` → "Insecure origins treated as secure" with `http://<ip>:8080`.

## Sharing

- **Web version:** send the folder or link to this repo. Others run `server.py` and open the tracker page. Nothing to install on the Quest.
- **APK later:** post on **SideQuest**. The official store requires applying through Meta's developer program; only worth it once something is finished.
