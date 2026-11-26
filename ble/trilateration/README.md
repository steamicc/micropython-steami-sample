# BLE trilateration indoor positioning

Three fixed beacons broadcast their name. A mobile board measures the signal strength (RSSI) of each beacon, converts it into a distance, computes its 2D position by trilateration and shows it as a dot on a map of the room.

## Hardware

- 4 STeaMi boards: 3 beacons and 1 mobile

## Run

Run the program on every board:

```bash
cd ble/trilateration
mpremote mount . run main.py
```

Pick the role with the D-PAD (**UP**/**DOWN**, **RIGHT** to confirm):

- **BEACON**: then choose `Beacon_M1`, `Beacon_M2` or `Beacon_M3`, and put the board at the position given in `BEACON_POS`.
- **MOBILE**: walk around; the screen shows the beacons (squares) and the estimated position (dot). **LEFT** returns to the menu.

## Processing chain

1. **RSSI average** over the last `RSSI_SAMPLES` packets of each beacon. A beacon not heard for 3 s is ignored.
2. **Distance** with the log-distance path loss model: `d = 10 ^ ((RSSI_REF - RSSI) / (10 * n))`, clamped to `MAX_DIST_CM`.
3. **Trilateration** by solving the two linear equations obtained by subtracting the circle equations; a result too far from the centre of the triangle is rejected.
4. **Exponential smoothing** of the position (`ALPHA`).
5. **Dead band**: the dot moves only when the smoothed position is more than `MIN_MOVE_CM` away from the displayed one.

## Calibration for your room

The values in the program come from the room where the example was written and must be measured again:

1. Measure the position of the beacons in centimetres and fill `BEACON_POS`, `SPACE_W` and `SPACE_H`.
2. Put the mobile board 1 m, then 2 m from each beacon. The mobile mode prints the averaged RSSI of each beacon every second on the serial console (`mpremote` shows it).
3. Fill `RSSI_REF` with the RSSI at 1 m and `PATH_LOSS_N` with `n = (RSSI_1m - RSSI_2m) / (10 × log10(2))`, about `(RSSI_1m - RSSI_2m) / 3`.

Measure with the mobile STeaMi itself: a phone does not report the same RSSI.

## What to observe

- Near a beacon, the position is accurate; in the middle of the triangle, it wanders by tens of centimetres.
- A person standing between the mobile and a beacon shifts the dot away from that beacon.
- With `ALPHA` close to 1, the dot jumps; close to 0, it lags behind.
