import aioble
import asyncio
import time

#  Buttons and Screen gestion
from machine import Pin
from steami import Screen
from steami_screen import DARK, WHITE
from xiaomi_ble import decode

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

# Maximum number of sensors kept in memory
MAX_SENSORS = 8

#constants
measurement = ["temperature", "humidity", "batteryLevel", "batteryPercentage"]
# BLE names of the sensors to follow; empty: every readable thermometer in range
allowed_devices = []

# variables
collected_data = {}  # address -> list of readings
sensor_names = {}  # address -> BLE name
captured_devices = 0
device_index = 0
measurement_index = 0

# Function to store the readings decoded by xiaomi_ble.decode()
def store_data(address, m):
    if address not in collected_data:
        if len(collected_data) >= MAX_SENSORS:
            return
        collected_data[address] = []

    collected_data[address].append({
        "time": "{:02d}:{:02d}:{:02d}".format(*time.localtime()[3:6]),  # MicroPython has no strftime
        "temperature": m["temperature"],
        "humidity": m["humidity"],
        "batteryLevel": m["voltage"],  # in volts
        "batteryPercentage": m["battery"],  # in %
    })

    if len(collected_data[address]) > MAX_DATA_PER_SENSOR:
        collected_data[address].pop(0)

    print("-> {}: {} C, {} %, battery {} %".format(
        sensor_names.get(address, address), m["temperature"], m["humidity"], m["battery"]))


# Function to scan for BLE devices and receive their data
async def scan_loop():
    print("---Starting Scan---")
    while True:
        async with aioble.scan(scan_duration, interval_us=scan_interval, window_us=scan_window, active=True) as scanner:
            async for result in scanner:
                # the service data of the pvvx formats (custom, atc1441, BTHome) is in the
                # advertising data; the BLE name may only come with the scan response
                m = decode(result.adv_data) or decode(result.resp_data)
                if m is None or m["format"] == "mibeacon":
                    continue
                address = m["mac"] or result.device.addr_hex().upper()
                name = result.name()
                if name:
                    sensor_names[address] = name
                if allowed_devices and sensor_names.get(address) not in allowed_devices:
                    continue
                store_data(address, m)
        await asyncio.sleep(scan_pause)  # Pause between scans

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
        address = list(collected_data.keys())[device_index]
        name = sensor_names.get(address, address[-8:])
        SCREEN.text(name, (text_x_center_position(name), u(30)))
        SCREEN.line(0, u(41), SCREEN.width - 1, u(41), DARK)

        # Display measurement
        # Get the selected measurement data, without the missing readings (None)
        measure = [entry[measurement[measurement_index]] for entry in collected_data[address]
                   if entry[measurement[measurement_index]] is not None]
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
        for fmt in ("{:.2f}", "{:.1f}", "{:.0f}"):  # fewer decimals when too wide
            min_text = fmt.format(min_measure) + " <"
            max_text = "> " + fmt.format(max_measure)
            if (len(min_text) + len(max_text)) * 8 + 4 <= SCREEN.width - 2 * u(6):
                break
        line_h = SCREEN.text_height() + u(2)  # text row + margin
        y = u(78) + u(2)
        SCREEN.text(min_text, (u(6), y))
        SCREEN.text(max_text, (SCREEN.width - u(6) - len(max_text) * 8, y))
        y += line_h

        # Display the last value received
        if measure:
            if measurement[measurement_index] == "temperature":
                unit = "C"
            elif measurement[measurement_index] == "batteryLevel":
                unit = "V"
            else:
                unit = "%"
            last_measure = f"{measurement[measurement_index][0].upper()}: {measure[-1]:.2f}{unit}"
            SCREEN.text(last_measure, (text_x_center_position(last_measure), y))

        # Display the time since the start of the program
        y += line_h - u(1)
        SCREEN.line(0, y, SCREEN.width - 1, y, DARK)
        duration = f"{int(time.time() - start_time)}s"
        SCREEN.text(duration, "S")

        SCREEN.show()
        await asyncio.sleep(1)

# Function to center the text drawn in (x, y): a cell is 8 px wide (x scale)
def text_x_center_position(text, scale=1):
    x_position = (SCREEN.width - len(text) * 8 * scale) // 2 # Center the text
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
