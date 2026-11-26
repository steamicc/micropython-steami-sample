# BLE RSSI proximity detector

Two boards run the same program. One advertises as a beacon, the other scans for it and turns the received signal strength (RSSI) into a 0–100 % proximity gauge.

## Hardware

- 2 STeaMi boards

## Run

Run the program on both boards:

```bash
cd ble/rssi_proximity
mpremote mount . run main.py
```

During the 10-second countdown shown at startup:

- hold the **UP** button of the D-PAD to start in **BEACON** mode;
- do nothing to start in **SCANNER** mode.

The beacon advertises as `Beacon_M1`, like the first beacon of the `hot_cold`, `room_mapper` and `trilateration` examples: a board left in beacon mode in any of these examples works here too.

## How it works

- The scanner keeps the advertisements named `Beacon_M1` and averages the last `RSSI_SAMPLES` RSSI values to reduce noise.
- The average is mapped linearly from `RSSI_MIN` (-90 dBm, far) to `RSSI_MAX` (-30 dBm, touching) onto 0–100 %.
- The gauge turns red above 70 %.

## What to observe

- Move the boards apart: the gauge drops, but not linearly with the distance (RSSI is logarithmic).
- Put a hand or a body between the boards: the RSSI drops without the distance changing.
- Increase `RSSI_SAMPLES`: the display gets steadier but reacts more slowly.
