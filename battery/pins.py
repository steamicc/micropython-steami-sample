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


def _in_circle(text, y, h):
    """True when text, centered, its cells h px high from row y, fits the circle."""
    cy = SCREEN.center[1]
    dy = max(abs(y - cy), abs(y + h - 1 - cy))
    return (len(text) * 8) ** 2 + 4 * dy * dy <= 4 * SCREEN.radius ** 2


def show_lines(lines, gap=2):
    """Draw text lines centered, stacked in the middle of the screen.

    Every line has the same size: the 8x8 font on 128 px, Spleen 8x16 on
    240 px (a cell is 8 px wide on both). gap: space between two lines, in
    eighths of the text height (2: 2 px on 128 px, 4 px on 240 px). On the
    round screen the gap shrinks, down to 0, until every line fits inside
    the circle.
    """
    h = SCREEN.text_height()
    n = len(lines)
    for g in range(gap, -1, -1):
        step = h + h * g // 8
        top = (SCREEN.height - (n - 1) * step - h) // 2
        if all(_in_circle(t, top + i * step, h) for i, t in enumerate(lines)):
            break
    for i, text in enumerate(lines):
        SCREEN.text(text, ((SCREEN.width - len(text) * 8) // 2, top + i * step))
