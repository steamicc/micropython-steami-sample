import asyncio
from time import sleep

from machine import Pin
from steami import Distance, Screen

# Screen: SSD1327 on V1a/V1b, GC9A01 on V1c. begin() as early as possible:
# the image memory is allocated at that moment.
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

def display_menu(list, index):
    SCREEN.menu(list, index)

def text_x_center_position(text, scale=1):
    # Center the text drawn in (x, y): a cell is 8 px wide (x scale)
    # on 128 px as on 240 px
    x_position = (SCREEN.width - len(text) * 8 * scale) // 2
    return x_position
