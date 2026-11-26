# BLE Personalised Thermometer  

This project is a BLE-based personalised thermometer that scans for specific BLE devices, collects temperature and humidity data, and displays the information on an OLED screen.  

## Features  
- **BLE Scanning**: Continuously scans for BLE devices and collects temperature and humidity data from allowed devices.  
- **Data Decoding**: Decodes the advertising data received from BLE sensors.  
- **OLED Display**: Displays the collected data, including graphs, on a 128x128 OLED screen.  
- **Button Interaction**: Allows switching between devices and measurements using buttons.  

## Requirements  
- **Hardware**:  
    - STM32WB55 microcontroller  
    - BLE-compatible sensors (e.g., Xiaomi Mijia LYWSD03MMC)  
    - 128x128 OLED display (SSD1327 driver)  
    - Two buttons for interaction  

- **Software**:  
    - MicroPython  
    - `aioble` library for BLE communication  
    - `ssd1327` library for OLED display  

## Parameters  
- **Scan Duration**: 250 ms  
- **Scan Interval**: 30,000 µs  
- **Scan Window**: 30,000 µs  
- **Scan Pause**: 0.1 seconds  

## How It Works  
1. **BLE Scanning**:  
     - The program scans for BLE devices within the allowed list (`chambre`, `salon`, `cuisine`).  
     - If valid data is received, it decodes the temperature and humidity values and stores them.  

2. **Data Display**:  
     - The OLED screen shows the current device, measurement graph, min/max values, and the last recorded value.  
     - The display updates every second.  

3. **Button Interaction**:  
     - Button A switches between devices.  
     - Button B switches between temperature and humidity measurements.  

## Compatibility with Xiaomi Mijia LYWSD03MMC  
This project supports Xiaomi Mijia LYWSD03MMC thermometers, including all six hardware versions.  

### Customizing Device Names  
The names of the thermometers can be personalized using the [TelinkMiFlasher](https://pvvx.github.io/ATC_MiThermometer/TelinkMiFlasher.html) tool. This allows you to configure the names to match the expected device names (`chambre`, `salon`, `cuisine`).  

### Configuration Steps  
1. Visit [ATC_MiThermometer](https://pvvx.github.io/ATC_MiThermometer).  
2. Follow the instructions to flash the compatible firmware.  
3. Use the configuration interface to set custom names for the devices.  

### Important Notes  
- Ensure the thermometers broadcast valid advertising data for proper detection and decoding.  
- The program is designed to work with BLE advertising packets from these devices.  

## Code Overview  
- **`decode_data(data, sensor_name)`**: Decodes temperature and humidity from BLE advertising data.  
- **`scan_loop()`**: Continuously scans for BLE devices and processes their data.  
- **`display_loop()`**: Updates the OLED display with the collected data.  
- **`button_pressed()`**: Handles button presses to switch devices or measurements.  
- **`main()`**: Runs the scanning, display, and button handling loops concurrently.  
