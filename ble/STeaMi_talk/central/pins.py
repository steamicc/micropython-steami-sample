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

def display_menu(devices, index):
    if not devices:
        SCREEN.text("No device", "CENTER")
        return
    names = [d.name() if hasattr(d, 'name') else str(d) for d in devices]
    # Sans le prefixe commun : sur 240 px, "> STeaMi-XXXX" serait coupe
    names = [n[len("STeaMi-"):] if n.startswith("STeaMi-") else n for n in names]
    SCREEN.menu(names, index)
