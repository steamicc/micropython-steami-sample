# 🛰️ STeaMi - BLE Distance Relay (1 Relay Scenario)

This MicroPython project demonstrates a Bluetooth Low Energy (BLE) network where **a sensor device** broadcasts a measured distance, a **relay node** processes the data, and an **actuator device** reacts (e.g., toggles a red LED) depending on the received value.

The relay acts as a gateway that receives sensor data via BLE advertising, interprets it, and forwards a control command (`LED ON` or `LED OFF`) to the actuator device.

---

## 📦 Features

* **BLE advertising and scanning** with `aioble`
* **1 sensor node (STeaMi-S)** broadcasting its measured distance
* **1 relay node (STeaMi-R)** scanning the sensor data, processing it, and forwarding a simplified control signal
* **1 actuator node (STeaMi-A)** listening for the relay’s command and toggling LEDs accordingly
* **OLED Display** showing local and received data
* Fully asynchronous design using `uasyncio`

---

## 🧠 System Architecture

1. `Sensor Node` → (advertising distance)
1. `Relay Node` → (advertising command)
1. `Actuator Node` → (LED ON/OFF)

---

## 🔁 How It Works

1. **Sensor Node (STeaMi-S)**
   * Reads distance from `DISTANCE.read()`.
   * Advertises the distance value in manufacturer data (`struct.pack("h", distance)`).

2. **Relay Node (STeaMi-R)**
   * Scans for nearby BLE devices named `STeaMi-S`.
   * When it receives a distance, it checks:
     * If `distance < 200 mm` → sends command `1` (LED ON)
     * Else → sends command `0` (LED OFF)
   * Advertises this command to the actuator node.

3. **Actuator Node (STeaMi-A)**
   * Scans for BLE advertisements from `STeaMi-R`.
   * Extracts the command byte and drives LEDs accordingly.
   * Displays recent received data.

---

## 🛠️ Requirements

* MicroPython-compatible board with BLE (e.g. **STM32WB55**, **ESP32-C3**)
* One display accessible as `display`
* One distance sensor accessible as `DISTANCE`
* Libraries:
  * `aioble` (BLE handling)
  * `uasyncio` (asynchronous tasks)
* Proper `pins.py` definitions:
  ```python
  DISTANCE = ...  # Object with .read()
  LED_RED = ...
  LED_GREEN = ...
  display = ...
---

## ⚙️ Parameters

| Variable | Purpose	| Default |
|----------|------------|---------|
| `SCAN_DURATION` | Scan time per BLE cycle (ms) | 500 |
| `ADV_TIMEOUT`	| Advertising time per cycle (ms) | 500 |

---

## 📋 Example Serial Output

Device name: STeaMi-R
BLE Task: Starting scan...
BLE Task: Scanning...
Received from STeaMi-S: 180 mm
BLE Task: Advertising command: LED ON
Advertisement done.

--- 

## 💡 Notes

- Adjust distance thresholds to tune LED activation sensitivity.
- Multiple sensors can coexist if their names are unique (STeaMi-S1, STeaMi-S2, ...).
- This system simulates a minimal BLE mesh relay behavior using advertising-only communication.
