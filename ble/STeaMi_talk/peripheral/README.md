# STeaMi BLE Distance Sensor

## Overview

This project implements a Bluetooth Low Energy (BLE) peripheral device using MicroPython, which periodically reads distance data from a VL53L1X time-of-flight sensor and broadcasts it to BLE clients. It also features a small display to show the device name, current distance, and connected clients. Button inputs allow cycling through connected devices.

## Features

* BLE advertising with dynamic device name (based on MAC address)
* Distance measurement using VL53L1X sensor
* OLED display for real-time data and menu interaction
* Client device name recognition over BLE
* Button control to navigate client list

## Hardware Requirements

* Microcontroller with BLE support (e.g. Pyboard D-series)
* VL53L1X time-of-flight sensor (I²C)
* SSD1327 OLED display (SPI)
* HTS221 (optional, I²C sensor included but not used in logic)
* APDS9960 (optional, I²C sensor included but not used in logic)
* 3 Buttons (A, B, Menu)
* RGB LEDs

## File Descriptions

* `main.py`: Main application logic for BLE communication, sensor reading, and UI handling.
* `pins.py`: Hardware initialization (buttons, sensors, display) and utility functions.

## Usage

1. Flash the firmware and upload both `main.py` and `pins.py`.
2. Power on the device.
3. It will start advertising via BLE with a unique device name.
4. Connect using a BLE client and send a name (UTF-8 string).
5. Distance updates are sent as BLE notifications.
6. Use buttons A/B to browse through connected device names on the screen.