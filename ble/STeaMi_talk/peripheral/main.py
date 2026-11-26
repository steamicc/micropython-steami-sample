from micropython import const
import asyncio
import aioble
import bluetooth
import struct
from pins import *

# UUIDs
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_DEVICE_NAME_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
_ADV_INTERVAL_MS = 250_000

# BLE setup
ble = bluetooth.BLE()
ble.active(True)
mac_bytes = ble.config('mac')[1]
mac_suffix = ''.join(f'{b:02X}' for b in mac_bytes[-2:])
device_name = f"STeaMi-{mac_suffix}"
print("Device name:", device_name)

# Global variables
distance = 0
connected_devices = []
devices_index = 0
client_name = "unknown"

# BLE service and characteristics
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
)
device_name_char = aioble.Characteristic(
    temp_service, _DEVICE_NAME_UUID, write=True, capture=True
)
aioble.register_services(temp_service)

# Encode distance as little-endian signed short
def _encode_distance(distance_mm):
    return struct.pack("<h", int(distance_mm))

# Task to read distance and update characteristic
async def sensor_task():
    global distance
    while True:
        distance = DISTANCE.read()
        temp_characteristic.write(_encode_distance(distance), send_update=True)
        await asyncio.sleep_ms(1000)

# Task to handle BLE peripheral functionality
async def peripheral_task():
    global client_name
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=device_name,
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)

            # Wait for client to write its name
            try:
                con,data = await device_name_char.written(timeout_ms=5000)
                client_name = data.decode()
                connected_devices.append(client_name)
                print("Client name received:", client_name)
            except asyncio.TimeoutError:
                print("No client name received.")

            await connection.disconnected(timeout_ms=None)
            connected_devices.remove(client_name)

# Task to handle display
async def display_task():
    global devices_index, connected_devices, device_name, distance, client_name
    while True:
        display.fill(0)
        display.text(device_name, text_x_center_position(device_name), 25, 255)
        display.text(f"{distance}mm", text_x_center_position(f"{distance}mm"), 45, 255)
        display_menu(connected_devices, devices_index)
        display.show()
        await asyncio.sleep(0.1)

# Task to handle button inputs
async def button_task():
    global devices_index, connected_devices
    while True:
        button = await wait_for_button()
        if button == "A":
            devices_index = (devices_index + 1) % len(connected_devices)
        elif button == "B":
            devices_index = (devices_index - 1) % len(connected_devices)
        elif button == "MENU":
            # Handle menu action here
            pass
        await asyncio.sleep(0.1)

# Main function to run all tasks
async def main():
    await asyncio.gather(
        sensor_task(),
        peripheral_task(),
        display_task(),
        button_task()
    )

asyncio.run(main())
