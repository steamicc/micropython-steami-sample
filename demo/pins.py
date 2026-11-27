import asyncio
import math
from time import sleep

from machine import Pin
from steami import Distance, Humidity, Light, Screen, Temperature
from steami_screen import WHITE

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
TEMPERATURE = Temperature()  # TEMPERATURE.read(): temperature in C
HUMIDITY = Humidity()  # HUMIDITY.read(): relative humidity in %
LIGHT = Light()  # LIGHT.read(): ambient light, raw count (V1a/V1b only)


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

def display_menu(name, list, index):
    SCREEN.clear()
    SCREEN.title(name, WHITE)
    SCREEN.menu(list, index)
    SCREEN.show()

def display_line(text, y, color=WHITE):
    """Draw text centred on row y (in 128 px units), cut to fit the screen.

    On the round 240 px screen of the V1c, the line keeps the characters
    that fit the circle at that row.
    """
    k = SCREEN.k
    y = SCREEN.u(y)
    room = SCREEN.width
    if k > 1:
        r = SCREEN.radius
        cy = SCREEN.center[1]
        d = max(abs(y - cy), abs(y + 8 * k - 1 - cy))
        room = 2 * int(math.sqrt(max(0, r * r - d * d))) - 2 * k
    text = text[: max(0, room) // (8 * k)]
    SCREEN.text(text, ((SCREEN.width - len(text) * 8 * k) // 2, y), color, k)
