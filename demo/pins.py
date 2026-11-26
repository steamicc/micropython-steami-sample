import asyncio
from time import sleep

import ssd1327

from machine import SPI, Pin
from steami import Distance, Humidity, Light, Temperature

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


spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")

display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

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
    display.fill(0)
    display.text(name, 45, 20, 255)
    for i, item in enumerate(list):
        if i == index:
            display.text(">", 35, ((i + 1) * 10)+30, 255)
        display.text(item , 45, ((i + 1) * 10)+30, 255)
    display.show()
