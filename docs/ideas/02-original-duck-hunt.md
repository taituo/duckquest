# 02 — Original Duck Hunt in an emulator

The original NES light gun (Zapper) doesn't work on modern TVs. Emulators that run on the Steam Deck (e.g. RetroArch, Mesen) can map the Zapper to the **mouse**.

## Plan

- The server turns the calibrated aim point into mouse movement and the trigger into a mouse click.
- On Linux / Steam Deck: a virtual mouse via `uinput` (e.g. `python-evdev`).
- The emulator then sees a normal mouse and the game works as-is.

## Notes

- Use a ROM of a game you own.
- Shares the "virtual input device" work with idea [07](07-super-wii-remote.md).
