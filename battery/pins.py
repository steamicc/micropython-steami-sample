import asyncio
from time import sleep
import time
import pyb

import ssd1327

from machine import SPI, Pin
from steami import Battery, Distance, Humidity, Temperature

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


spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")

display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)
