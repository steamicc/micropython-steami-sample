"""BLE beacon advertising example using aioble and SSD1327 OLED.

Broadcasts a BLE advertisement containing the board name and a live
temperature reading from the WSEN-PADS sensor. The beacon is visible
from any BLE scanner app (nRF Connect, LightBlue, etc.).

Hardware:
    - STM32WB55 BLE radio
    - SSD1327 128x128 OLED display (round)
    - WSEN-PADS pressure + temperature sensor

BLE payload:
    - Complete Local Name: "STeaMi-XXXX" (last 2 bytes of MAC address)
    - Manufacturer Specific Data: temperature as int16 (x100, in 0.01 C)
"""

import sys

sys.path.insert(0, "/remote")

import bluetooth
import struct
import uasyncio as asyncio

import aioble
import ssd1327
from machine import I2C, SPI, Pin
from steami_screen import GRAY, GREEN, LIGHT, Screen, SSD1327Display, WHITE
from wsen_pads import WSEN_PADS

# === BLE setup ===
ble = bluetooth.BLE()
ble.active(True)

mac_bytes = ble.config("mac")[1]
mac_suffix = "".join(f"{b:02X}" for b in mac_bytes[-2:])
DEVICE_NAME = f"STeaMi-{mac_suffix}"
print("Device name:", DEVICE_NAME)

# === Display ===
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = SSD1327Display(ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs))
screen = Screen(display)

# === Sensor ===
i2c = I2C(1)
pads = WSEN_PADS(i2c)

# === BLE parameters ===
ADV_INTERVAL_US = 200_000  # 200 ms between advertisements
ADV_TIMEOUT_MS = 500  # advertise for 500 ms per cycle
SENSOR_INTERVAL_MS = 1000  # read sensor every 1 second

# === Shared state ===
temperature = 0.0


def build_adv_payload(name, temp_raw):
    """Build a BLE advertising payload.

    Contains:
        - Complete Local Name (type 0x09)
        - Manufacturer Specific Data (type 0xFF): int16 temperature x100
    """
    payload = bytearray()

    # Complete Local Name
    name_bytes = name.encode()
    payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes

    # Manufacturer Specific Data: temperature encoded as int16 (x100)
    man_data = struct.pack("h", temp_raw)
    payload += bytes((len(man_data) + 1, 0xFF)) + man_data

    return payload


async def sensor_task():
    """Read temperature from WSEN-PADS every second."""
    global temperature
    while True:
        try:
            temperature = pads.temperature()
        except Exception as e:
            print("Sensor error:", e)
        await asyncio.sleep_ms(SENSOR_INTERVAL_MS)


async def ble_task():
    """Advertise BLE beacon with device name and temperature."""
    while True:
        # Encode temperature as int16 (multiply by 100 to keep 2 decimals)
        temp_raw = int(temperature * 100)
        adv_payload = build_adv_payload(DEVICE_NAME, temp_raw)

        try:
            await aioble.advertise(
                interval_us=ADV_INTERVAL_US,
                adv_data=adv_payload,
                connectable=False,
                timeout_ms=ADV_TIMEOUT_MS,
            )
        except asyncio.TimeoutError:
            pass  # Normal: non-connectable advertisement timeout

        await asyncio.sleep_ms(100)


async def display_task():
    """Update OLED display with current beacon state."""
    while True:
        screen.clear()
        screen.title("BLE BEACON")
        screen.value(f"{temperature:.1f}", unit="C")
        screen.subtitle(DEVICE_NAME, "Advertising...")
        screen.show()
        await asyncio.sleep_ms(500)


async def main():
    await asyncio.gather(
        sensor_task(),
        ble_task(),
        display_task(),
    )


asyncio.run(main())
