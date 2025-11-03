import asyncio
from time import sleep
from pyb import Pin

import ssd1327

from machine import SPI, Pin, I2C
import machine
from vl53l1x import VL53L1X
from hts221 import HTS221
from apds9960 import uAPDS9960 as APDS9960
from bq27441 import BQ27441

LED_RED = Pin("LED_RED", Pin.OUT_PP)
LED_GREEN = Pin("LED_GREEN", Pin.OUT_PP)
LED_BLUE = Pin("LED_BLUE", Pin.OUT_PP)

A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

SPEAKER = Pin("SPEAKER", Pin.OUT_PP)

i2c = I2C(1)
DISTANCE = VL53L1X(i2c)
SENSOR = HTS221(i2c)
apds = APDS9960(i2c)

fg = BQ27441(i2c)

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

def display_menu(list, index):
    for i, item in enumerate(list):
        if i == index:
            display.text(">", 15, ((i + 1) * 10)+55, 255)
        display.text(item , 25, ((i + 1) * 10)+55, 255)

def text_x_center_position(text):
    x_position = (128 - (len(text) * 8) ) // 2 # Center the text
    return x_position