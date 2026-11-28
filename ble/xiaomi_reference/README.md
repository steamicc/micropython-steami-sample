# BLE reference thermometer (Xiaomi LYWSD03MMC)

The board compares its own temperature and humidity with those of a Xiaomi
LYWSD03MMC thermo-hygrometer placed next to it, received over BLE. The screen
shows both readings and their difference, so a photo of the board is enough
to check its sensors.

## Hardware

- 1 STeaMi board
- 1 Xiaomi LYWSD03MMC with the [pvvx firmware](https://github.com/pvvx/ATC_MiThermometer),
  in any of its advertising formats: "custom" (pvvx), "atc1441" or
  unencrypted BTHome v2. The original Xiaomi firmware encrypts its data: the
  program reports it but cannot read it.

## Run

```bash
cd ble/xiaomi_reference
mpremote mount . run main.py
```

Leave the board and the sensor side by side for about ten minutes before
comparing: the board warms up while running, and the two sensors do not
react at the same speed.

## Screen

| Line | Content |
| --- | --- |
| Board | temperature and humidity measured by the board |
| sensor name | temperature and humidity received from the Xiaomi |
| RH at Tb | humidity the reference air would have at the board temperature (Tb) |
| Difference | board minus reference: temperature, then board humidity minus "RH at Tb" |
| bottom | RSSI of the sensor and age of its last frame, in seconds |

"--" marks a missing reading.

## How it works

- **Decoding**: `xiaomi_ble.py` reads the service data (AD type 0x16) of the
  advertising frame rather than fixed byte offsets, so the three pvvx formats
  are recognised whatever else the frame contains.
- **Sensor choice**: with `TARGET = ""` the program follows the Xiaomi with
  the best RSSI heard in the last 30 seconds, in practice the one next to the
  board. It keeps it until another one is heard at least 6 dB stronger, so it
  does not jump between two sensors placed side by side. Set `TARGET` to a MAC
  address or a BLE name to force one.
- **Humidity at the board temperature**: the board heats its own sensor, which
  then measures warmer, and so relatively drier, air than the room. For the
  same amount of water vapour the relative humidity drops when the temperature
  rises (Magnus formula). Comparing the board humidity with "RH at Tb" removes
  this effect and leaves only the sensor error.
- **CSV log**: every 5 seconds the serial console receives
  `t_s;address;rssi;format;T_ref;RH_ref;T_board;RH_board;RH_ref_at_T_board`.
  Record it with `mpremote mount . run main.py | tee test.csv`.

## Expected accuracy

Typical values from the manufacturers' datasheets:

| Sensor | Temperature | Humidity |
| --- | --- | --- |
| Xiaomi LYWSD03MMC (Sensirion SHTC3 in most batches) | ±0.2 °C | ±2 % RH |
| STeaMi V1c (Bosch BME280) | ±0.5 °C (±1 °C over the range) | ±3 % RH |
| STeaMi V1a, V1b (Würth WSEN-HIDS) | ±0.2 °C | ±1.8 % RH |

In a 10-minute test on a V1c (screen on, continuous BLE scan), two Xiaomi
sensors agreed within 0.15 °C and 1 % RH, while the board read about 4.3 °C
above the air: most of the temperature difference is the board heating itself.
Its humidity was about 11 % RH below the Xiaomi readings, and about 4 % RH
below once brought to the board temperature.
