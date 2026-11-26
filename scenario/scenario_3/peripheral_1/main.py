import uasyncio as asyncio
from peripheral_base import run
from pins import LED_GREEN

asyncio.run(run("STeaMi-P1", LED_GREEN))
