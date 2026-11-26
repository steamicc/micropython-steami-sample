# DEMO

This project is a menu-driven embedded system built for the STeaMi. It's designed to showcase and experiment with embedded peripherals and BLE capabilities.

---

## 🧩 Project Structure

| File             | Description                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------------- |
| `main.py`        | Entry point for the system; launches the main interactive menu.                                         |
| `pins.py`        | Hardware configuration: initializes GPIO pins, I2C/SPI peripherals, sensors, display, and buttons.      |
| `ble.py`         | Menu and logic for BLE operations: scan nearby devices, emit advertisements.                            |
| `advertizing.py` | Asynchronous BLE advertising and scanning logic. Manages local and remote distance broadcasting.        |
| `led.py`         | Toggles onboard RGB LEDs with menu selection.                                                           |
| `buzzer.py`      | Plays melodies using the speaker with animated circular progress on display.                            |
| `button.py`      | Captures and displays button presses in real time.                                                      |
| `sensors.py`     | Reads temperature, humidity, distance, and light levels, then displays them.                            |
| `screen.py`      | Showcases graphics capabilities: font rendering, grayscale patterns, 3D animation, and emoji pixel art. |
| `gesture.py`     | Gesture detection with the APDS-9960 (V1a/V1b only; shows "No sensor" on a V1c).              |

---

## 📟 Features

### 🧭 Menu Navigation

* A/B buttons: Scroll up/down through options
* MENU button: Select or exit a module
* Display: OLED 128x128 using `ssd1327` via SPI

### 📡 BLE Module

* Each device advertises its measured distance.
* Asynchronously scans for other `STeaMi` devices and logs their distances.
* Custom BLE payload encoding using manufacturer data.

### 🌡 Sensors

* **VL53L1X**: Time-of-Flight distance sensor.
* **Temperature and humidity**: WSEN-HIDS on V1a/V1b, BME280 on V1c (through `steami`).
* **APDS-9960**: Ambient light, V1a/V1b only (0 on a V1c).
* Values updated and displayed in real time.

### 🎵 Buzzer

* Interactive sound menu with multiple tunes:

  * Happy
  * Sad
  * Epic
  * Pirates of the Caribbean (almost)
* Circular animated progress bar around the display perimeter during playback.

### 💡 LEDs

* Toggle RED, GREEN, and BLUE LEDs individually.

### ⬛ Screen Demos

* **TEXT**: ASCII characters with visual encoding.
* **GRAY**: Grayscale bar chart.
* **ANIM**: Rotating cube rendered using 3D projections.
* **STEAMI**: Pixel-art animation of a smiley face.

### 🕹 Buttons

* Displays button inputs in real time.

---

## 🔌 Hardware Requirements

* Microcontroller with:

  * BLE support
  * GPIO pins
  * SPI and I2C buses
* Components:

  * OLED 128x128 SPI (SSD1327)
  * VL53L1X (distance)
  * WSEN-HIDS (V1a/V1b) or BME280 (V1c): humidity/temperature
  * APDS-9960 (light, V1a/V1b only)
  * 3 tactile buttons (A, B, MENU)
  * 3 LEDs (RED, GREEN, BLUE)
  * Speaker/Buzzer

---

## 🚀 Getting Started

1. Flash the entire project onto your board.
2. Boot the system; the main menu will appear.
3. Use the A and B buttons to scroll through modules.
4. Press MENU to enter a module.
5. Press MENU again to return to the main menu.

---

## ⚠ Known Limitations

* On a V1c, the screen stays black (no GC9A01 support in MicroPython yet, see micropython-steami-lib#368), and the light and gesture sensors are missing: the demo still runs and prints its menu on the serial console.
* BLE scan and advertising work asynchronously but might be affected by timing or radio interference.