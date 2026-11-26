import uasyncio as asyncio
from peripheral_base import run
from pins import *
asyncio.run(run("STeaMi-P3", "STeaMi-R3", LED_BLUE))
