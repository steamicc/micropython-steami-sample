# STeaMi BLE talk

## Overview

This project implements a complete BLE-based system using MicroPython, consisting of:

* A **Peripheral Device** ("STeaMi-\*"): Measures distance using a VL53L1X sensor and broadcasts it over BLE.
* A **Central Device** ("Client-\*"): Scans for peripheral devices, connects to one, and displays the received distance data.


## Features

### Peripheral (`main.py` in **peripheral mode**):

* BLE advertising with dynamic device name (`STeaMi-XX`)
* Sends distance data over BLE (VL53L1X)
* Displays device name, distance, and connected clients
* Accepts client device names via BLE
* Buttons to navigate connected device list

### Central (`main.py` in **central mode**):

* Scans for BLE devices named `STeaMi-*`
* Connects and sends its own name to the peripheral
* Receives and displays distance data in real-time
* Buttons to navigate device list and initiate connection

## Hardware Requirements

* Microcontroller with BLE and MicroPython support
* VL53L1X distance sensor (I²C)
* SSD1327 OLED display (SPI)
* Buttons: A, B, Menu
* Optional: HTS221, APDS9960 (included in setup but not essential)

## How to Use

### Peripheral Mode

1. Load the **peripheral version** of `main.py` onto one board.
2. Power on — it starts advertising BLE with a dynamic name.
3. Connect using a central device — it will display distance data.

### Central Mode

1. Load the **central version** of `main.py` onto another board.
2. Power on — it starts scanning for peripherals named `STeaMi-*`.
3. Use buttons:

   * **A/B**: Navigate found devices
   * **MENU**: Connect/disconnect
4. Once connected, it displays the distance received from the peripheral.