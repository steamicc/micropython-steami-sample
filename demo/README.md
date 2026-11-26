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
| `gesture.py`     | Gesture detection using APDS9960 (non-functional).                                            |

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
* **HTS221**: Temperature and humidity.
* **APDS9960**: Ambient light (gesture sensor partially implemented).
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
  * HTS221 (humidity/temperature)
  * APDS9960 (light/gesture)
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

* `gesture.py` is marked as **BROKEN** and doesn't currently provide gesture detection.
* BLE scan and advertising work asynchronously but might be affected by timing or radio interference.