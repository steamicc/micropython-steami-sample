"""BLE beacon advertising example using aioble and SSD1327 OLED.

Broadcasts a BLE advertisement containing the board name and a live
temperature reading from the WSEN-PADS sensor. The beacon is visible
from any BLE scanner app (nRF Connect, LightBlue, etc.).

Hardware:
    - STM32WB55 BLE radio
    - SSD1327 128x128 OLED display (round)
    - WSEN-PADS pressure + temperature sensor

BLE payload:
    - Flags: LE General Discoverable, BR/EDR not supported
    - Complete Local Name: "STeaMi-XXXX" (last 2 bytes of MAC address)
    - Manufacturer Specific Data: company ID 0xFFFF (reserved for tests),
      then the temperature as a little-endian int16 (x100, in 0.01 C)
"""

import bluetooth
import struct
import uasyncio as asyncio

import aioble
import ssd1327
from machine import I2C, SPI, Pin
from steami_screen import Screen, SSD1327Display
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

# Manufacturer Specific Data must start with a 16-bit company identifier.
# 0xFFFF is reserved by the Bluetooth SIG for tests and prototypes.
COMPANY_ID = 0xFFFF

# === Shared state ===
temperature = 0.0


def build_adv_payload(name, temp_raw):
    """Build a BLE advertising payload.

    Each field is encoded as: length (1 byte), type (1 byte), data.
    The length counts the type byte plus the data.

    Contains:
        - Flags (type 0x01)
        - Complete Local Name (type 0x09)
        - Manufacturer Specific Data (type 0xFF): company ID, then
          temperature x100 as int16
    """
    payload = bytearray()

    # Flags: 0x02 = LE General Discoverable, 0x04 = BR/EDR not supported
    payload += bytes((2, 0x01, 0x06))

    # Complete Local Name
    name_bytes = name.encode()
    payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes

    # Manufacturer Specific Data: BLE is little-endian ("<"), so the
    # company ID (uint16 "H") and the temperature (int16 "h") use "<Hh".
    man_data = struct.pack("<Hh", COMPANY_ID, temp_raw)
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
