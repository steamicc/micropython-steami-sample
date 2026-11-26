import bluetooth
import uasyncio as asyncio
import aioble
import struct
from time import ticks_ms, ticks_diff
from pins import * 

# === Initialisation BLE ===
ble = bluetooth.BLE()
ble.active(True)

device_name = f"STeaMi-S"
print("Device name:", device_name)

# === Paramètres du BLE ===
SCAN_DURATION = 3_000
ADV_TIMEOUT = 1_000

# === Données ===
local_distance = 0
devices_distances = {}
energy_current = 0  # en mA

# === Fonctions auxiliaires ===
def advertising_payload(name=None, manufacturer_data=None):
    payload = bytearray()
    if name:
        name_bytes = name.encode()
        payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes
    if manufacturer_data:
        payload += bytes((len(manufacturer_data) + 1, 0xFF)) + manufacturer_data
    return payload

def extract_manufacturer_data(adv_bytes):
    i = 0
    while i < len(adv_bytes):
        length = adv_bytes[i]
        if length == 0:
            break
        type_ = adv_bytes[i + 1]
        if type_ == 0xFF:
            return adv_bytes[i + 2 : i + 1 + length]
        i += 1 + length
    return None

def text_x_center(text):
    return max((128 - len(text) * 8) // 2, 0)

# === Tâches ===
async def ble_task():
    while True:
        print("BLE Task: Advertising...")
        man_data = struct.pack("h", local_distance)
        adv_payload = advertising_payload(name=device_name, manufacturer_data=man_data)
        try:
            await aioble.advertise(
                interval_us=150_000,
                adv_data=adv_payload,
                connectable=False,
                timeout_ms=ADV_TIMEOUT
            )
            print("Advertisement done.")
        except asyncio.TimeoutError:
            print("Advertisement timeout (non-connectable).")
            pass
        await asyncio.sleep_ms(200)

async def sensor_task():
    global local_distance
    while True:
        local_distance = DISTANCE.read()
        await asyncio.sleep(1)

async def energy_task():
    global energy_current
    while True:
        energy_current = fg.current_average()
        await asyncio.sleep(1)

async def display_task():
    while True:
        display.fill(0)
        display.text(device_name, text_x_center(device_name), 50, 255)
        display.text(f"Me: {local_distance}", text_x_center("Me: XXX"), 60, 255)
        display.text(f"I: {energy_current:.1f} mA", text_x_center("I: XXXXX"), 70, 255)
        display.show()
        await asyncio.sleep(0.5)

async def main():
    await asyncio.gather(
        sensor_task(),
        ble_task(),
        energy_task(),
        display_task()
    )

asyncio.run(main())