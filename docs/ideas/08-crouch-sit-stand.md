# 08 — Crouch / sit / stand detection

The Quest knows each controller's **height**, so crouching or sitting drops your hands and the game can notice.

## Problem

Hand height alone can't tell crouching from just lowering the arms.

## Solutions

- **Both hands:** both controllers dropping together and staying down → probably a crouch.
- **Body calibration:** stand normally, then crouch; the game remembers both heights per player (works for adults and kids).
- **Button clutch:** hold a button while changing posture so the game treats it as body movement. Most reliable.
- **Chest-mounted Quest:** the Quest's own height is the body height, no guessing.
- **Overhead Quest:** hands closer to the stand = standing, farther = crouching.

## Try it now

DuckQuest debug view (D): the middle number in `p=[x, y, z]` is height in metres.
