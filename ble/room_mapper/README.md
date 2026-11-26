# BLE RSSI room mapper

Records the signal strength (RSSI) of 2 or 3 fixed beacons at several points of a room. The measurements are saved in a CSV file on the DAPLink flash, readable from the computer through the USB drive of the board. This is the data-collection step of radio fingerprinting, and the data used to calibrate the `trilateration` example.

## Hardware

- 3 or 4 STeaMi boards: 2 or 3 beacons and 1 scanner

## Run

Run the program on every board:

```bash
cd ble/room_mapper
mpremote mount . run main.py
```

Pick the role with the D-PAD (**UP**/**DOWN**, **RIGHT** to confirm):

- **BEACON**: then choose `Beacon_M1`, `Beacon_M2` or `Beacon_M3`. Place the beacons in a triangle around the room. **LEFT** returns to the menu.
- **SCANNER**: walk around with the board. Each **RIGHT** press records one point; **LEFT** stops and saves.

Starting the scanner mode erases the flash: copy `RSSI_MAP.CSV` from the board's USB drive before starting a new session.

## CSV format

```
point_id,beacon_name,rssi
1,Beacon_M1,-62
1,Beacon_M2,-71
1,Beacon_M3,-80
2,Beacon_M1,-58
```

A beacon not heard during the last `RSSI_MAX_AGE_MS` (3 s) is shown as `---` and is not recorded.

## Calibration

Two boards at the same distance may report different RSSI values. Put the scanner against each beacon in turn and fill `RSSI_OFFSET` so that the three beacons read the same value.

## What to observe

- Record several points at the same place: RSSI varies by several dB between measurements.
- Compare the values with a person standing between the scanner and a beacon.
