# STeaMi BLE Central Scanner

## Overview

This MicroPython project implements a BLE **central device** that scans for peripherals broadcasting under the name `STeaMi-*`, connects to one, writes its own name to a writable characteristic, and displays received distance data on an OLED screen. It uses button inputs to navigate and select among discovered devices.

## Features

- BLE scanning for devices with names starting with "STeaMi"
- Connects and writes client name to BLE peripheral
- Reads distance data via BLE and displays it
- OLED screen showing device info and measurements
- Button control to select and connect to peripherals

## Hardware Requirements

- Microcontroller with BLE support (e.g. Pyboard D-series)
- SSD1327 OLED display (SPI)
- Buttons (A, B, Menu)
- RGB LEDs
- Optional I²C sensors (VL53L1X, HTS221, APDS9960 — initialized but not used directly)

## File Descriptions

- `main.py`: Manages BLE scanning, connection, communication, and UI logic.
- `pins.py`: Handles hardware setup for display, sensors, and button input.

## Usage

1. Flash and upload both `main.py` and `pins.py` to your board.
2. Power on the device. It will begin scanning for BLE peripherals.
3. Use button **A/B** to browse devices found.
4. Press **MENU** to connect to a selected device.
5. Sends its own device name, then receives and displays the distance.
6. Press **MENU** again to disconnect and resume scanning.