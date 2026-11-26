import uasyncio as asyncio
from peripheral_base import run
from pins import *
asyncio.run(run("STeaMi-P2", "STeaMi-R2", LED_RED))
