import asyncio
from time import sleep
import time
import pyb
from pyb import Pin

import ssd1327

from machine import SPI, Pin, I2C
from vl53l1x import VL53L1X
from hts221 import HTS221
from apds9960 import uAPDS9960 as APDS9960
from bq27441 import BQ27441

LED_RED = pyb.LED(1)
LED_GREEN = pyb.LED(2)
LED_BLUE = pyb.LED(3)

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