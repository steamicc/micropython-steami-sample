# BLE hot/cold treasure hunt

A "hot or cold" game for two boards. One board hides as the **treasure** (a BLE beacon), the other is the **seeker**: it measures the signal strength (RSSI) of the treasure and tells the player whether they are getting closer, with a face on the screen and beeps that speed up.

## Hardware

- 2 STeaMi boards

## Run

Run the program on both boards:

```bash
cd ble/hot_cold
mpremote mount . run main.py
```

At startup, pick the role with the D-PAD: **UP**/**DOWN** to select, **RIGHT** to confirm (SEEKER is selected automatically after 10 seconds). **LEFT** returns to the menu at any time.

## Zones

| Zone | Proximity | Face | Sound |
| --- | --- | --- | --- |
| COLD | 0–25 % | sad | 1 low beep every 3 s |
| WARM | 25–50 % | sleeping | 1 beep every 1.2 s |
| HOT | 50–75 % | happy | 2 fast beeps every 500 ms |
| BURNING | 75–100 % | love | 3 rapid beeps every 150 ms |

While the treasure is not found, the seeker shows a surprised face and plays a short beep every second.

## How it works

- **Smoothing**: an exponential moving average (`EMA_ALPHA`) reacts quickly to large RSSI jumps and damps small fluctuations.
- **Hysteresis**: the proximity must cross a zone boundary by `ZONE_HYSTERESIS` % before the zone changes, so the display and the sound do not flicker at the boundaries.
- **Buzzer**: the tones use the hardware PWM (Timer 1, channel 4 on the `SPEAKER` pin), so scanning and display keep running while a beep plays.
- **Calibration**: adjust `RSSI_MAX` (boards 1–2 cm apart) and `RSSI_MIN` (boards about 5 m apart) to your room; the seeker prints the smoothed RSSI on the serial console when the zone changes.

The treasure advertises as `Beacon_M1`, like the beacons of the other localization examples.
