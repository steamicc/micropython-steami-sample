# 🛰️ STeaMi - BLE Distance Sharing Network

This MicroPython project enables multiple embedded devices to broadcast their own sensor distance via Bluetooth Low Energy (BLE), and display distances received from nearby peers.

Each device:

* Reads its distance from a sensor (`DISTANCE.read()`)
* Advertises its distance via BLE with a unique device name
* Scans for other devices with the `STeaMi-XXXX` prefix
* Displays its own and nearby devices’ distances on an attached screen

---

## 📦 Features

* **Bluetooth Low Energy (BLE)** advertising & scanning using `aioble`
* **Unique device names** based on MAC suffix (e.g., `STeaMi-4B9E`)
* **Local distance reading**
* **Distance broadcasting** every cycle via manufacturer-specific data
* **Display** of:

  * Local distance
  * Up to 4 most recently detected nearby STeaMi devices

---

## 🛠️ Requirements

* MicroPython-compatible board with BLE support (e.g. STM32WB55)
* Display module (e.g. OLED, I2C-based) accessible as `display`
* Distance sensor accessible as `DISTANCE`
* `aioble` library for BLE communication
* `uasyncio` for cooperative multitasking

Make sure `pins.py` defines:

```python
DISTANCE = ...  # Object with .read()
display = ...   # Object with .text(), .fill(), .show()
```

---

## 🔁 How It Works

1. **Device Initialization**
   Each device builds its unique name: `STeaMi-XXXX`, using its MAC address.

2. **BLE Scanning**
   Periodically scans for nearby BLE devices advertising with the prefix `STeaMi`.

3. **BLE Advertising**
   After scanning, each device advertises its current distance encoded in manufacturer data.

4. **Distance Parsing**
   Received distances are parsed and stored along with timestamps.

5. **Display Task**

   * Shows local distance at the top
   * Displays up to 4 most recently seen peers with their distances

---

## 📋 Customization

* Change `SCAN_DURATION` and `ADV_TIMEOUT` to adjust BLE timing.
* Adjust screen layout, fonts, or positions for different displays.
* Enable device expiration by uncommenting the `purge_old_devices()` function.

---

## 📎 Example Output on Serial

```
Device name: STeaMi-4B9E
BLE Task: Starting scan...
BLE Task: Scanning...
Received from STeaMi-2E02: 114 cm
BLE Task: Advertising...
Advertisement done.
```