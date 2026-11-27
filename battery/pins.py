import asyncio
from time import sleep
import time
import math
import pyb

from machine import Pin
from steami import Battery, Distance, Humidity, Screen, Temperature

# The screen (SSD1327 on V1a/V1b, GC9A01 on V1c). begin() allocates the
# image memory, so it comes first, before the other objects use the RAM.
SCREEN = Screen()
SCREEN.begin()

LED_RED = pyb.LED(1)
LED_GREEN = pyb.LED(2)
LED_BLUE = pyb.LED(3)

A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

SPEAKER = Pin("SPEAKER", Pin.OUT_PP)

# Sensors: steami picks the right chip for the board release
# (V1a, V1b or V1c). Creating them touches no hardware.
DISTANCE = Distance()  # DISTANCE.read(): distance in mm
TEMPERATURE = Temperature()  # TEMPERATURE.read(): temperature in C
HUMIDITY = Humidity()  # HUMIDITY.read(): relative humidity in %
BATTERY = Battery()  # BATTERY.current(): average current in mA


def show_lines(lines, pitch=10):
    """Draw text lines centered, stacked in the middle of the screen.

    pitch: distance between two rows, in 128 px units. The text is scaled
    by SCREEN.k; on the round 240 px screen a line too wide for its row is
    shrunk until it fits inside the circle.
    """
    k = SCREEN.k
    step = SCREEN.u(pitch)
    cy = SCREEN.center[1]
    y = (SCREEN.height - ((len(lines) - 1) * step + 8 * k)) // 2
    for text in lines:
        f = k
        while f > 1:
            dy = max(abs(y - cy), abs(y + 8 * f - cy))
            half = math.sqrt(max(0, SCREEN.radius ** 2 - dy ** 2))
            if len(text) * 8 * f <= 2 * half:
                break
            f -= 1
        x = (SCREEN.width - len(text) * 8 * f) // 2
        SCREEN.text(text, (x, y + 4 * (k - f)), scale=f)
        y += step
