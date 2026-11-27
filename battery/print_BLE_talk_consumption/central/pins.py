import asyncio
from time import sleep
import time

from machine import Pin
from steami import Battery, Distance, Screen

# The screen (SSD1327 on V1a/V1b, GC9A01 on V1c). begin() allocates the
# image memory, so it comes first, before the other objects use the RAM.
SCREEN = Screen()
SCREEN.begin()

LED_RED = Pin("LED_RED", Pin.OUT_PP)
LED_GREEN = Pin("LED_GREEN", Pin.OUT_PP)
LED_BLUE = Pin("LED_BLUE", Pin.OUT_PP)

A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

SPEAKER = Pin("SPEAKER", Pin.OUT_PP)

# Sensors: steami picks the right chip for the board release
# (V1a, V1b or V1c). Creating them touches no hardware.
DISTANCE = Distance()  # DISTANCE.read(): distance in mm
BATTERY = Battery()  # BATTERY.current(): average current in mA


async def wait_for_button():
    while True:
        if A_BUTTON.value() == 0:
            await asyncio.sleep(0.2)
            return "A"
        elif B_BUTTON.value() == 0:
            await asyncio.sleep(0.2)
            return "B"
        elif MENU_BUTTON.value() == 0:
            await asyncio.sleep(0.2)
            return "MENU"
        await asyncio.sleep(0.1)

def display_menu(devices, index):
    if not devices:
        SCREEN.text("No device", "CENTER")
        return
    names = [d.name() if hasattr(d, 'name') else str(d) for d in devices]
    SCREEN.menu(names, index)

def text_x_center_position(text):
    x_position = (SCREEN.width - len(text) * 8) // 2  # Center the text (8 px cells)
    return x_position
