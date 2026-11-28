# BLE examples

## BLE localization path

These examples build on each other, from a single beacon to indoor positioning. They all use `aioble` and `steami_screen`, both frozen in the STeaMi firmware. The beacons of the last four examples share the `Beacon_M1`/`Beacon_M2`/`Beacon_M3` names, so a board left in beacon mode works with all of them.

| Example | Boards | What it teaches |
| --- | --- | --- |
| [`beacon/`](beacon/) | 1 + phone | Advertising payload: name and sensor data |
| [`rssi_proximity/`](rssi_proximity/) | 2 | RSSI as a proxy for distance, averaging |
| [`hot_cold/`](hot_cold/) | 2 | Smoothing, hysteresis, sound feedback |
| [`room_mapper/`](room_mapper/) | 3–4 | Data collection, RSSI variability, CSV on the DAPLink flash |
| [`trilateration/`](trilateration/) | 4 | Path loss model, trilateration, position filtering |

## Other examples

- [`STeaMi_adv/`](STeaMi_adv/) — share distance readings between boards through BLE advertising
- [`STeaMi_talk/`](STeaMi_talk/) — central and peripheral exchanging data over a BLE connection
- [`Thermometer_Scanner/`](Thermometer_Scanner/) — collect temperature and humidity from nearby BLE sensors
- [`xiaomi_reference/`](xiaomi_reference/) — compare the board temperature and humidity with a Xiaomi LYWSD03MMC received over BLE

## Troubleshooting

### BLE timeout on STeaMi

If you encounter a **timeout or failure** when calling:

```python
from bluetooth import BLE
BLE().active(True)
```

This may be due to a missing or incompatible BLE firmware on your STM32WB chip.

#### ✅ Solution:

To resolve this issue, you need to update the wireless stack of your STeaMi device. Follow these steps:

1. Visit the following website to download and update the wireless stack:  
   [Update STeaMi Wireless Stack](https://steamicc.github.io/steami-tools/webusb-wireless-stack/index.html)

2. On the site, you will find the necessary tools and instructions to update the firmware and the BLE stack on your STM32WB device.

3. Once updated, you should be able to activate BLE without any issues.

After flashing the firmware, BLE should activate without issues:

```python
>>> from bluetooth import BLE
>>> BLE().active(True)
True
```

This will fix the BLE activation timeout issue on the STeaMi board.