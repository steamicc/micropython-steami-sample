import bluetooth
import uasyncio as asyncio
import aioble
import struct
from time import ticks_ms
from pins import *

ble = bluetooth.BLE()
ble.active(True)

device_name = f"STeaMi-R"
print("Device name:", device_name)

SCAN_DURATION = 500
ADV_TIMEOUT = 500

devices_distances = {}
energy_current = 0
forwarded_distance = None

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

async def ble_task():
    global forwarded_distance
    while True:
        print("BLE Task: Starting scan...")
        async with aioble.scan(SCAN_DURATION, interval_us=30000, window_us=30000, active=True) as scanner:
            print("BLE Task: Scanning...")
            async for result in scanner:
                name = result.name()
                if name and name.startswith("STeaMi") and name != device_name:
                    man_data = extract_manufacturer_data(result.adv_data)
                    if man_data and len(man_data) == 2:
                        distance, = struct.unpack("h", man_data)
                        devices_distances[name] = (distance, ticks_ms())
                        print(f"Received from {name}: {distance} cm")
                        if name.startswith("STeaMi-S"):
                            forwarded_distance = distance

        await asyncio.sleep_ms(SCAN_DURATION + 50)

        print("BLE Task: Advertising...")
        if forwarded_distance is not None:
            if forwarded_distance > 300:
                man_data = struct.pack("b", 0)
                LED_RED.on()
            else:
                man_data = struct.pack("b", 1)
                LED_GREEN.on()
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
            finally:
                LED_RED.off()
                LED_GREEN.off()
                forwarded_distance = None
            await asyncio.sleep_ms(200)

async def energy_task():
    global energy_current
    while True:
        energy_current = fg.current_average()
        await asyncio.sleep(1)

async def display_task():
    while True:
        display.fill(0)
        display.text(device_name, text_x_center(device_name), 10, 255)

        recent_devices = sorted(
            devices_distances.items(),
            key=lambda item: item[1][1],
            reverse=True
        )[:3]

        y = 30
        for name, (dist, _) in recent_devices:
            display.text(f"{name[-4:]}: {dist}", text_x_center("XXXX: XXX"), y, 255)
            y += 10

        display.text(f"I: {energy_current:.1f} mA", text_x_center("I: XXXXX"), y + 5, 255)
        display.show()
        await asyncio.sleep(0.5)

async def main():
    await asyncio.gather(
        ble_task(),
        display_task(),
        energy_task()
    )

asyncio.run(main())
