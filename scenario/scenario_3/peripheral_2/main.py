import uasyncio as asyncio
from peripheral_base import run
from pins import LED_RED

asyncio.run(run("STeaMi-P2", LED_RED))
