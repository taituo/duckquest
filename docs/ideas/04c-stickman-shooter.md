# 04c — Stickman shooter: wrist aims

A side-view shooter where the controller's tilt is the aim.

## Controls

- **Wrist angle → aim direction**: point up to shoot up, level forward, down to shoot down. The controller's tilt becomes a 2D aiming angle.
- **Trigger** → shoot
- **Thumbstick** → walk and jump
- **Grip** → grab or block

## Why it's robust

Aiming needs only the controller's **angle**, not its position. Angle comes from the controller's own motion sensors, so aiming keeps working even when the cameras briefly lose sight of the hand. The most forgiving idea on the list.

## Two players

Same mirroring as [04](04-side-view-sword-duel.md).

## Needed

The tracker page doesn't send thumbstick axes yet. Small addition: `gamepad.axes[2]` and `[3]`.
