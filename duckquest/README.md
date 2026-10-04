# DuckQuest

A retro duck-shooting game for the TV, aimed with Meta Quest 3 controllers. The Quest sits still facing the players and tracks the controllers. The controllers are the guns.

```
Quest 3 (quest.html, WebXR) --Wi-Fi--> server.py --WebSocket--> game.html on the TV
                                          ^
                  Steam Deck buttons --> padbridge.py (optional)
```

## Setup

You need Python 3 (no packages), a browser for the TV, and a Quest 3 on the same Wi-Fi.

1. On the computer that will run the game (a Steam Deck in Desktop Mode, a PC or a Mac) run `python3 server.py` in this folder. It prints two addresses.
2. On the TV, open `http://localhost:8080` (or `http://<computer-ip>:8080` from another device). Press **F** for fullscreen.
3. In the Quest Browser open the printed `https://<ip>:8443/quest.html`. Accept the certificate warning (Advanced, then Proceed), press **Start tracking**, and allow the immersive session.
4. Put the Quest down facing the players and cover its proximity sensor with tape so it stays awake.
5. Calibrate (below), then pick a game from the menu.

If the Deck is the TV screen and you develop on a Mac, see `../CLAUDE.md` and `../scripts/deck.sh`.

## Menu

Shoot a choice, or use the D-pad and Start (or the arrow keys and Enter):

- **Normal game** · ducks and the dog
- **Specials** · **Bear hunt**: bears only, three lives
- **Princess party** · four balloon levels and a birthday finale (`?name=Lauri` puts a name on the cake)
- **Calibrate** · starts calibration for the controller you shot with

## Calibration

Calibration is separate for each controller, one player at a time, and you never need a keyboard:

1. **P1 (left controller):** from where you play, aim at the top-left, top-right, bottom-right and bottom-left corners of the picture, pulling the trigger at each. Then aim at the bullseye.
2. **P2 (right controller):** the same, as its own step. **Start** or **B** skips a controller.

Use only the controller named on screen. The screen shows each controller's pointing direction, tracking quality and trigger so you can see that it is tracked. Pick up a controller that lies on the table; resting controllers fall asleep.

Re-tune one controller without redoing the corners: **K** or D-pad left (P2), **J** (P1). The result is saved in `calib.json` with backups in `calib-backups/`. Open the game with `?restore` to reload the saved calibration.

## Controls

| | Quest controllers | Steam Deck | Keyboard / mouse |
|---|---|---|---|
| Shoot | trigger | A, RT or RB | left click |
| Reload | grip, or aim off-screen and shoot | LT, LB, B or X | right click |
| Change weapon | A / X during play | Y | W, Tab, middle click |
| Calibrate | A / X on the title screen | D-pad up (P1), D-pad left (P2) | C (P1), K (P2) |
| Finish or skip | B / Y | Start | Enter |
| Back | | Back (Select) | Esc |
| Mirror the calibration view | | D-pad right | V |
| Debug overlay | | D-pad down | D |
| Music on/off, retro or smooth graphics | | | M, G |

Left controller = P1 (blue), right controller = P2 (orange), Deck or mouse = P3 (white). The pistol holds six shots. The shotgun fires three pellets with a slower pump, and the machine gun fires about 12 shots a second while the trigger is held.

## Screenshots

Add `?demo=` to the address to jump to a scene: `title`, `menu`, `specials`, `normal`, `dog`, `bear`, `party1`, `party4`, `finale`.

## Troubleshooting

- **No "Proceed" option on the cert warning:** in the Quest Browser open `chrome://flags`, enable "Insecure origins treated as secure", add `http://<ip>:8080`, then open `http://<ip>:8080/quest.html`.
- **Controllers show NOT SEEN:** wake them by picking them up and keep them in the headset's view. Check that **Start tracking** is still running.
- **Tracking stops when the headset is off:** the proximity sensor isn't fully covered. Set the sleep timer to the longest option, or run `../scripts/quest.sh wake` over adb.
- **The Steam Deck's buttons do nothing in the game:** Steam Input hides them from the browser in Desktop Mode. Run `../scripts/deck.sh pad`, which starts `padbridge.py` on the Deck.
- **No sound:** browsers block audio until the page is allowed to play. In Firefox set `media.autoplay.default` to `0`. The game also retries by itself.
- **Aim drifts or is offset:** the headset moved or was recentered. Recalibrate.
- **Jittery aim:** more light, 1.5 to 2.5 m from the Quest, controllers in view. Check the pose rate and the worst gap with the debug overlay (**D**). Running the server on the game machine removes one Wi-Fi hop.
- **Debugging the Quest page without adb:** its errors and events are printed in the server terminal as `[quest ...]` lines.
