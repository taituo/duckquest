# 01 — DuckQuest ✅

**Status:** built, tested in simulation (not yet with a real Quest). Code in [`/duckquest`](../../duckquest/).

A modern take on light-gun duck shooting. Controllers are the guns; the Quest sits in front of the players as a tracker.

## Features

- Two players (left / right controller) plus mouse for testing
- 6 shells; reload by aiming off-screen and pulling the trigger
- Rounds of 10 ducks with a hit quota, golden ducks (500 pts), combo multipliers, perfect-round bonus
- Controller vibration on shots and hits
- Synthesised sound, procedural graphics, four times of day
- Debug view (D) with raw positions and pose age

## Calibration

- **Aim mode (default, C or A/X):** from your seat, aim at the four screen corners, then at a bullseye with each controller. Works wherever the TV is relative to the Quest. Simulation: within ~0.1%, also with the hand moved 10 cm.
- **Touch mode (T):** touch the controller tip to three corners. Most exact, needs the Quest to see the controller at the TV.

## Next steps

- Test with a real Quest: placement, lighting, smoothness
- Tune the smoothing filter if aim is jittery or laggy
