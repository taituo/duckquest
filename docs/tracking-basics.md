# How Quest tracking works

- Each Quest 3 controller has hidden **infrared lights** in a known pattern. The headset's cameras see the pattern and calculate the controller's exact position and angle.
- Each controller also has **motion sensors** inside. They fill in fast movements and short moments when the cameras lose sight of it. During those moments the pose is marked as "emulated" (shown as `EMULATED` in the DuckQuest debug view).
- The headset also tracks **itself** in the room with its cameras.

## Which controller is which

Controllers are paired over Bluetooth as **left** and **right**, so they never get mixed up, even when swapped between hands or strapped to a head. DuckQuest uses left = P1, right = P2.

## Limits

- Only **one left and one right controller** at a time. No third controller.
- No add-on trackers (pucks) like some other VR systems.
- **Bare hands** can be tracked instead of controllers, usually not both at once, and less precise for aiming.
- More tracked things → a **second Quest**.
- The Quest itself is required: the controllers can't track themselves without the headset's cameras.

## What the tracker page sends

Per controller, many times per second: position, orientation (quaternion), trigger, grip, A/X and B/Y buttons, movement speed of the grip, and whether the pose is emulated. Thumbstick axes are not sent yet (needed for idea 04c).

## Check it yourself

In DuckQuest press **D**. The middle number in `p=[x, y, z]` is the controller's height in metres.
