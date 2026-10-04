# BoxQuest 3 (experiment)

A first-person boxing game in the spirit of *4D Sports Boxing*, played with Quest controllers. Each controller is a glove: a ball on a sleeve that is attached to you at the bottom of the screen. It uses the same relay server as DuckQuest.

Open `http://<server>:8080/boxing/boxing.html` (the Quest tracker page must be running), or choose **Specials, Boxing** in the DuckQuest menu.

## How to play

| Move | How |
|---|---|
| Punch | move a glove fast toward the opponent (jab, cross, hook: the speed and place of the hit count) |
| Block | keep both gloves up in front of your face; a glove meeting the opponent's punch blocks it |
| Step and side-step | thumbstick (forward/back, left/right); stepping aside dodges a punch |
| Calibrate | hold **A** or **X** for a second, standing ready with the gloves up and still |
| Start | Enter, or **B / Y** on a controller |

Three rounds of 60 seconds, or a knockout. The opponent gets faster each round. Hits to the head count more than hits to the body.

Without a Quest: move the mouse (right glove), click to punch, **J** / **K** for left and right punches, **A D W S** to step.

## Version 2

- **Tracking tip:** hold each controller with the **black ring turned toward the Quest**. The cameras see the ring's infrared lights, and tracking is much better that way. The game warns when a controller is only guessing from its motion sensors ("WEAK TRACKING", the glove fades and gets a red ring).
- Smoother gloves with a motion trail, and punch types: jab, cross, hook (sideways swing), uppercut (upward), with combos that add damage.
- The opponent throws jabs, hooks and body shots, sometimes in chains, and gives a yellow flash on the side the punch comes from. Body shots must be blocked with a low glove.
- Knockdowns: three knockdowns are a K.O. He gets up with less health after each.
- The first round calibrates automatically if a controller is not calibrated yet.
- Keys: **F** flips forward, **M** mirrors left and right (both are remembered).

## Version 3: pixel art with modern light

- The scene is drawn at 384x216 (x5 on a 1080p TV) with soft shading, then snapped to the ENDESGA 32 palette with 4x4 ordered dithering. Bloom on lights, light beams with dust, a crowd that jumps and flashes cameras, a neon sign.
- Opponents are built from a posed 3D skeleton: shaded, outlined body, face with expressions, bruises and a cut as he takes damage, kneeling knockdowns with stars and a count, a timber fall on K.O. Three opponents take turns (**N** picks the next on the title screen).
- Hit-stop, white flash and spark bursts on hits, sweat spray, speed lines on combos, slow motion on knockdowns, confetti when you win. When you are knocked out the camera drops to the canvas.
- A 5x7 pixel font HUD: fighting-game health bars with a damage trail, knockdown pips, round clock.
- The gloves also move on the title screen, so you can check the tracking before the fight.
- **P** turns the palette filter off and **G** the glow (if the frame rate is low). `?demo=title|fight|wind|hit|down|ko|lose` shows a scene without the Quest.
