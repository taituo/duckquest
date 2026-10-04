# Keeping the Quest awake while not worn

1. **Cover the proximity sensor** between the lenses with tape or a folded sticky note. The headset then thinks it's being worn. This is the main fix.
2. **Longest sleep / display-off timer** in the Quest settings (menu names change between system updates).
3. **Keep it charging** with a USB-C cable. Tracking with the screen on lasts about 2 hours on battery.
4. **Stationary boundary** where it sits, so boundary warnings don't pause tracking. In developer mode the boundary can be turned off.
5. **Don't press the Meta button** while playing: the menu pauses the tracking page. A long press recenters, which breaks calibration.
6. **Airflow**: it gets warm running for a long time without being worn.

## Developer-mode alternative to tape

```
adb shell am broadcast -a com.oculus.vrpowermanager.prox_close
```

Resets when the headset restarts. Tape is simpler and works the same.
