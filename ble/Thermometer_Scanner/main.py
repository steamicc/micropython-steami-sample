import aioble
import asyncio
import struct
import time

#  Buttons and Screen gestion
from machine import SPI, Pin
import ssd1327
A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)

spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

# parameters
scan_duration = 250  # in ms
scan_interval = 30000  # in us
scan_window = 30000  # in us
scan_pause = 0.1  # in seconds

# Paramètre : nombre maximum de mesures stockées par capteur
MAX_DATA_PER_SENSOR = 100

#constants
measurement = ["temperature", "humidity", "batteryLevel", "batteryPercentage"]
allowed_devices = ["Nord", "Sud", "Est", "Ouest", "Maison"]

# variables
collected_data = {}
captured_devices = 0
device_index = 0
measurement_index = 0

# Function to decode the advertising data received from the sensors
def decode_data(data, sensor_name):
    print(f"Raw data {data}")

    for i in range(len(data)):
        print(f"Raw data [{i}]: {data[i]}")
        if i < len(data)-1:
            print(f"Raw data [{i}:{i+2}] in hex : {struct.unpack("<h", data[i:i+2])[0]}")

    temperature = struct.unpack("<h", data[13:15])[0] / 100 # in °C
    humidity = struct.unpack("<h", data[16:18])[0] / 100 # in %
    batteryLevel = struct.unpack("<h", data[0:2])[0] / 100 # in Volts (A revoir car données incohérentes)
    batteryPercentage = data[11] # in %

     # Get the current time
    current_time = time.strftime("%H:%M:%S", time.localtime())

    if sensor_name not in collected_data:
        collected_data[sensor_name] = []

    collected_data[sensor_name].append({
        "time": current_time,
        "temperature": temperature,
        "humidity": humidity,
        "batteryLevel": batteryLevel,
        "batteryPercentage": batteryPercentage
    })

    if len(collected_data[sensor_name]) > MAX_DATA_PER_SENSOR:
        collected_data[sensor_name].pop(0)

    print(f"-> Sensor: {sensor_name} - Temperature:{temperature:.2f} C, Humidity: {humidity:.2f} %, Battery Level: {batteryLevel:.2f} V, Battery Percentage: {batteryPercentage:.2f} %, at {current_time}")


# Function to scan for BLE devices and receive their data tend to fill the memory in 10 min
async def scan_loop():
    print(f"---Starting Scan---")
    while True:
        async with aioble.scan(scan_duration, interval_us=scan_interval, window_us=scan_window, active=True) as scanner:
            async for result in scanner:
                if result.name() in allowed_devices:
                    print(f"======> Found sensor : {result.name()}")
                    if result.adv_data:
                        if (len(result.adv_data) > 17):  # Check if received complete data
                            decode_data(result.adv_data, result.name())
                        else:
                            print(f"==> Invalid data length")
                    else:
                        print("==> no adv_data")
            asyncio.sleep(scan_pause)  # Pause between scans

# Function to display the data on the screen
async def display_loop():
    global captured_devices
    start_time = time.time()

    while True:
        display.fill(0)
        
        if not collected_data:
            scanning_text = "Scanning ..."
            display.text(scanning_text, text_x_center_position(scanning_text), 60, 255)
            display.show()
            await asyncio.sleep(2)
            continue
        
        # Display the device name and the index of captured devices
        captured_devices = len(collected_data)
        captured_devices_text = f"{device_index+1}/{captured_devices}"
        display.text(captured_devices_text, text_x_center_position(captured_devices_text), 10, 255)

        # Display selected device name
        name = list(collected_data.keys())[device_index]
        display.text(name, text_x_center_position(name), 20, 255)
        display.framebuf.line(0, 30, 128, 30, 100)

        # Display measurement
        measure = [entry[measurement[measurement_index]] for entry in collected_data[name]] # Get the selected measurement data
        max_measure = max(measure) if measure else 0
        min_measure = min(measure) if measure else 0
        # Draw the graph
        if max_measure != min_measure and len(measure) > 1:
            length = len(measure)
            for i in range(1, length):
                x1 = int((i - 1) * 127 / (length - 1))
                y1 = 80 - int((measure[i - 1] - min_measure) / (max_measure - min_measure) * 45)
                x2 = int(i * 127 / (length - 1))
                y2 = 80 - int((measure[i] - min_measure) / (max_measure - min_measure) * 45)

                display.framebuf.line(x1, y1, x2, y2, 255)
        else:
            display.framebuf.line(0, 60, 127, 60, 255) # Draw a horizontal line if no data

        # Display the min and max values
        display.framebuf.line(0, 80, 128, 80, 100)
        display.text(f"{min_measure:.2f} <", 5, 85, 255)
        display.text(f"> {max_measure:.2f}", 65, 85, 255)

        # Display the last value received
        if collected_data[name]:
            if measurement[measurement_index] == "temperature":
                unit = "C"
            elif measurement[measurement_index] == "batteryLevel":
                unit = "V"
            else:
                unit = "%"
            last_measure = f"{measurement[measurement_index][0].upper()}: {collected_data[name][-1][measurement[measurement_index]]:.2f}{unit}"
            display.text(last_measure, text_x_center_position(last_measure), 100, 255)

        # Display the time since the start of the program
        display.framebuf.line(0, 110, 128, 110, 100)
        duration = f"{int(time.time() - start_time)}s"
        display.text(duration, text_x_center_position(duration), 115, 255)

        display.show()
        await asyncio.sleep(1)

# Function to center the text on the display
def text_x_center_position(text):
    x_position = (128 - (len(text) * 8) ) // 2 # Center the text
    return x_position

# Function to handle button presses and change the displayed device or measurement
async def button_pressed():
    global device_index, measurement_index
    while True:
        if A_BUTTON.value() == 0: # change device
            device_index += 1
            if device_index >= captured_devices: device_index = 0
        elif B_BUTTON.value() == 0: # change measurement
            measurement_index += 1
            if measurement_index >= len(measurement): measurement_index = 0
        await asyncio.sleep(0.1)

# Main function to run the scan and display loops concurrently
async def main():
    data_task = asyncio.create_task(scan_loop())
    display_task = asyncio.create_task(display_loop())
    button_task = asyncio.create_task(button_pressed())
    await asyncio.gather(data_task, display_task, button_task)


asyncio.run(main())