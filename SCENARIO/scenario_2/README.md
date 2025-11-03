# 🛰️ STeaMi - BLE Distance Relay (1 Relay Scenario)

This MicroPython project extends the previous **1-relay BLE distance network** into a **2-relay topology**.  
It demonstrates how BLE advertising and scanning can be chained to form a simple **multi-hop mesh**, allowing data to propagate even when the sensor and actuator are not directly reachable.


---

## 📦 Features

* **2 relays** creating a bridge between sensor and actuator
* **Multi-hop BLE advertising** — data flows across multiple nodes
* **Threshold-based LED activation**
* **Real-time display** of device names and distances
* Fully asynchronous architecture using `uasyncio`

---

## 🧠 System Architecture

1. `Sensor Node` → (advertising distance)
1. `Relay Node 1` → (advertising command)
1. `Relay Node 2` → (advertising command)
1. `Actuator Node` → (LED ON/OFF)

---

## 🔁 How It Works

1. **Sensor Node (STeaMi-S)**
   * Continuously measures distance via `DISTANCE.read()`.
   * Advertises the measured value via BLE manufacturer data (`struct.pack("h", distance)`).

2. **First Relay (STeaMi-R1)**
   * Scans for `STeaMi-S` advertisements.
   * On reception, checks if the distance is below the threshold (e.g., 200 mm).
   * Forwards this value to the second relay using BLE advertising.

3. **Second Relay (STeaMi-R2)**
   * Scans for `STeaMi-R1` advertisements.
   * Extracts and retransmits the control signal to the actuator node.

4. **Actuator Node (STeaMi-A)**
   * Scans for relay commands (`b"\x01"` or `b"\x00"`).
   * Turns **LED_RED ON** if `b"\x01"`, **OFF** otherwise.
   * Displays received relay data for debugging or visualization.

---

## 🛠️ Requirements

* 4 MicroPython boards with BLE support:
  * 1 Sensor node (STeaMi-S)
  * 2 Relay nodes (STeaMi-R1, STeaMi-R2)
  * 1 Actuator node (STeaMi-A)
* OLED display on each board (optional but recommended)
* Distance sensor on the Sensor node
* Proper `pins.py` definitions for each board
* `aioble` and `uasyncio` libraries

---

## ⚙️ BLE Flow Summary

| Node | Receives From | Advertises To | Data Type |
|------|----------------|---------------|------------|
| `STeaMi-S` | — | `STeaMi-R1` | distance (2 bytes) |
| `STeaMi-R1` | `STeaMi-S` | `STeaMi-R2` | processed command (1 byte) |
| `STeaMi-R2` | `STeaMi-R1` | `STeaMi-A` | forwarded command (1 byte) |
| `STeaMi-A` | `STeaMi-R2` | — | executes LED control |

---

## 📋 Example Serial Output

Device name: STeaMi-R1
BLE Task: Scanning...
Received from STeaMi-S: 145 mm
Forwarding command: LED ON
BLE Task: Advertising...
Advertisement done.

Device name: STeaMi-R2
Received from STeaMi-R1: LED ON
Forwarding to actuator...

--- 

## 💡 Notes

* This setup illustrates a **BLE mesh-like topology** built purely from advertisements — no BLE connections required.
* Relays can be chained indefinitely to extend range, at the cost of propagation delay.
* All timing (`SCAN_DURATION`, `ADV_TIMEOUT`) can be tuned to balance responsiveness and energy consumption.

---

## 🧭 Tips

* For debugging, use unique device names (`STeaMi-S`, `STeaMi-R1`, `STeaMi-R2`, `STeaMi-A`).
* Use the display task to visualize nearby devices and data.
* Test in sequence: start the sensor → relay 1 → relay 2 → actuator.