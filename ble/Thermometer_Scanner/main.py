import aioble
import asyncio
import struct
import time

#  Buttons and Screen gestion
from machine import Pin
from steami import Screen
from steami_screen import DARK, WHITE

# Screen: SSD1327 on V1a/V1b, GC9A01 on V1c. begin() as early as possible:
# the image memory is allocated at that moment.
SCREEN = Screen()
SCREEN.begin()

A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)

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
            print(f"Raw data [{i}:{i+2}] in hex : {struct.unpack('<h', data[i:i+2])[0]}")

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
    print("---Starting Scan---")
    while True:
        async with aioble.scan(scan_duration, interval_us=scan_interval, window_us=scan_window, active=True) as scanner:
            async for result in scanner:
                if result.name() in allowed_devices:
                    print(f"======> Found sensor : {result.name()}")
                    if result.adv_data:
                        if (len(result.adv_data) > 17):  # Check if received complete data
                            decode_data(result.adv_data, result.name())
                        else:
                            print("==> Invalid data length")
                    else:
                        print("==> no adv_data")
            asyncio.sleep(scan_pause)  # Pause between scans

# Function to display the data on the screen
async def display_loop():
    global captured_devices
    start_time = time.time()
    u = SCREEN.u
    k = SCREEN.k

    while True:
        SCREEN.clear()

        if not collected_data:
            SCREEN.text("Scanning ...", "CENTER")
            SCREEN.show()
            await asyncio.sleep(2)
            continue

        # Display the device name and the index of captured devices
        captured_devices = len(collected_data)
        captured_devices_text = f"{device_index+1}/{captured_devices}"
        SCREEN.text(captured_devices_text, "N")

        # Display selected device name
        name = list(collected_data.keys())[device_index]
        SCREEN.text(name, (text_x_center_position(name), u(30)), scale=k)
        SCREEN.line(0, u(41), SCREEN.width - 1, u(41), DARK)

        # Display measurement
        measure = [entry[measurement[measurement_index]] for entry in collected_data[name]] # Get the selected measurement data
        max_measure = max(measure) if measure else 0
        min_measure = min(measure) if measure else 0
        # Draw the graph (between y = u(46) and y = u(74), x within the circle)
        graph_x = u(6)
        graph_w = u(122) - graph_x
        graph_bottom = u(74)
        graph_h = u(28)
        if max_measure != min_measure and len(measure) > 1:
            length = len(measure)
            for i in range(1, length):
                x1 = graph_x + int((i - 1) * graph_w / (length - 1))
                y1 = graph_bottom - int((measure[i - 1] - min_measure) / (max_measure - min_measure) * graph_h)
                x2 = graph_x + int(i * graph_w / (length - 1))
                y2 = graph_bottom - int((measure[i] - min_measure) / (max_measure - min_measure) * graph_h)

                for d in range(k):  # line k px thick
                    SCREEN.line(x1, y1 + d, x2, y2 + d, WHITE)
        else:
            SCREEN.line(graph_x, u(60), graph_x + graph_w, u(60), WHITE) # Draw a horizontal line if no data

        # Display the min and max values
        SCREEN.line(0, u(78), SCREEN.width - 1, u(78), DARK)
        min_text = f"{min_measure:.2f} <"
        max_text = f"> {max_measure:.2f}"
        scale = k  # glyph factor: 1 when both texts do not fit side by side
        while scale > 1 and (len(min_text) + len(max_text)) * 8 * scale + 4 > SCREEN.width - 2 * u(6):
            scale -= 1
        y = u(80) + 4 * (k - scale)
        SCREEN.text(min_text, (u(6), y), scale=scale)
        SCREEN.text(max_text, (SCREEN.width - u(6) - len(max_text) * 8 * scale, y), scale=scale)

        # Display the last value received
        if collected_data[name]:
            if measurement[measurement_index] == "temperature":
                unit = "C"
            elif measurement[measurement_index] == "batteryLevel":
                unit = "V"
            else:
                unit = "%"
            last_measure = f"{measurement[measurement_index][0].upper()}: {collected_data[name][-1][measurement[measurement_index]]:.2f}{unit}"
            SCREEN.text(last_measure, (text_x_center_position(last_measure), u(90)), scale=k)

        # Display the time since the start of the program
        SCREEN.line(0, u(99), SCREEN.width - 1, u(99), DARK)
        duration = f"{int(time.time() - start_time)}s"
        SCREEN.text(duration, "S")

        SCREEN.show()
        await asyncio.sleep(1)

# Function to center the text on the display (glyphs scaled by SCREEN.k)
def text_x_center_position(text):
    x_position = (SCREEN.width - (len(text) * 8 * SCREEN.k)) // 2 # Center the text
    return x_position

# Function to handle button presses and change the displayed device or measurement
async def button_pressed():
    global device_index, measurement_index
    while True:
        if A_BUTTON.value() == 0: # change device
            device_index += 1
            if device_index >= captured_devices:
                device_index = 0
        elif B_BUTTON.value() == 0: # change measurement
            measurement_index += 1
            if measurement_index >= len(measurement):
                measurement_index = 0
        await asyncio.sleep(0.1)

# Main function to run the scan and display loops concurrently
async def main():
    data_task = asyncio.create_task(scan_loop())
    display_task = asyncio.create_task(display_loop())
    button_task = asyncio.create_task(button_pressed())
    await asyncio.gather(data_task, display_task, button_task)


asyncio.run(main())
