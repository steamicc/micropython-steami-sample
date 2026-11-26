import uasyncio as asyncio
from peripheral_base import run
from pins import LED_BLUE

asyncio.run(run("STeaMi-P3", LED_BLUE))
