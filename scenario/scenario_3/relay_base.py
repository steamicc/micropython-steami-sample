"""Relay node of scenario 3.

A relay listens to every node, and re-advertises under its own name each new
message, with one more hop. Together the relays form a mesh: a message from
P1 reaches P2 even when P2 is out of range of P1.
"""

import uasyncio as asyncio
import aioble
from mesh import MAX_HOPS, NODES, decode, encode, is_new
from pins import *

SCAN_MS = 800  # Listen for 800 ms...
ADV_MS = 300  # ...then re-advertise each new message for 300 ms


async def ble_task(device_name):
    print(f"Relay {device_name} active")
    last_seq = {}

    while True:
        # === Collect the new messages ===
        to_forward = []
        async with aioble.scan(SCAN_MS, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                name = result.name()
                if not name or name == device_name or name not in NODES:
                    continue
                message = decode(result.adv_data)
                if not message:
                    continue
                src, dst, seq, hop, value = message
                if src == device_name or hop >= MAX_HOPS or not is_new(last_seq, src, seq):
                    continue
                to_forward.append(message)

        # === Forward them, one more hop ===
        for src, dst, seq, hop, value in to_forward:
            print(f"{device_name} relays {value} mm from {src} to {dst} (hop {hop + 1})")
            try:
                await aioble.advertise(
                    interval_us=100_000,
                    adv_data=encode(device_name, src, dst, seq, hop + 1, value),
                    connectable=False,
                    timeout_ms=ADV_MS,
                )
            except asyncio.TimeoutError:
                pass  # Normal end of a non-connectable advertisement


async def display_task(name):
    while True:
        display.fill(0)
        display.text(name, 10, 20, 255)
        display.text("Relay mesh node", 10, 35, 255)
        display.show()
        await asyncio.sleep(0.5)


async def run(device_name):
    await asyncio.gather(ble_task(device_name), display_task(device_name))
