# 06 — Switching adventure: TV ↔ VR

An adventure game where you can switch between playing on the TV and wearing the Quest, in the same world.

## How it could work

- The **game world lives on the computer**; the TV and the Quest page both show it.
- **Headset on the stand** → tracker mode, play on the TV with the controllers.
- **Headset on the head** → same page switches to full VR.
- **Switch detection:** a still headset = tracker mode, one moving like a head = VR mode. Button as backup.
- Game state is shared, so you continue exactly where you were.

## Game ideas

- **Dive in:** explore a small diorama world from above on the TV; put on the headset and you're shrunk down inside it at full scale.
- **Two views of one puzzle:** some clues only on the big screen, others only in VR up close or behind things.
- **Family play:** one person in VR as the explorer, others watch the map on the TV and guide them (using a gamepad or the Deck, since the explorer has both controllers).

## First prototype

One small 3D room shown on the TV in window mode ([05](05-tv-as-window.md)) and in VR on the Quest, with the switch working both ways.
