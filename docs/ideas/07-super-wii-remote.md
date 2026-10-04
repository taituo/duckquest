# 07 — "Super Wii remote" for any game

The server turns the Quest tracking into a **virtual gamepad or mouse** on the computer. Steam and other games then see a normal controller, so aiming, swinging or tilting could control existing games, not just ours.

Compared with the originals: the Wii only knew roughly where its remote pointed, and Kinect saw the body but not fine hand movement. This knows each controller's exact position and angle.

## Plan

- Linux / Steam Deck: `uinput` virtual devices (e.g. `python-evdev`) → mouse for light-gun games, gamepad sticks for tilt/swing.
- Windows: a virtual gamepad driver would be needed.
- Mapping profiles per game (pointer, tilt-to-stick, swing-to-button).

## Related

[02](02-original-duck-hunt.md) uses the mouse part of this.
