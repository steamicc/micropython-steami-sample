# BLE beacon

Broadcasts a non-connectable BLE advertisement carrying the board name and the temperature measured by the WSEN-PADS sensor. The OLED screen shows the name and the current temperature.

First step of the BLE localization path: the other examples (`rssi_proximity`, `hot_cold`, `room_mapper`, `trilateration`) measure the signal strength of such advertisements.

## Hardware

- 1 STeaMi board
- A phone with a BLE scanner app (nRF Connect, LightBlue, etc.)

## Run

```bash
cd ble/beacon
mpremote mount . run main.py
```

## Advertising payload

| Field | Type | Content |
| --- | --- | --- |
| Flags | `0x01` | `0x06`: LE General Discoverable, BR/EDR not supported |
| Complete Local Name | `0x09` | `STeaMi-XXXX` (last 2 bytes of the MAC address) |
| Manufacturer Specific Data | `0xFF` | company ID `0xFFFF` (reserved for tests), then temperature × 100 as a little-endian `int16` |

In nRF Connect, the manufacturer data of a board at 21.37 °C reads `0xFFFF` as company and `0x5908` as data: `0x0859` = 2137.

## What to observe

- The beacon appears in the scanner app under its `STeaMi-XXXX` name.
- Warm the sensor with a finger: the manufacturer data changes within a second.
