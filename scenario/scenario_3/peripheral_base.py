"""Peripheral node of scenario 3.

A peripheral measures a distance and sends it to the next peripheral of the
chain (P1 -> P2 -> P3 -> P1), through the relays. It listens to the relays
for the messages addressed to it, and lights its LED when the distance
received is below THRESHOLD_MM.
"""

import random

import uasyncio as asyncio
import aioble
from mesh import NODES, decode, encode, is_new
from pins import *

THRESHOLD_MM = 300
ADV_MS = 500  # Advertise each message for 500 ms...
SCAN_MS = 1000  # ...then listen to the relays for 1 s


def next_peripheral(name):
    """P1 sends to P2, P2 to P3 and P3 to P1."""
    peripherals = [n for n in NODES if n.startswith("STeaMi-P")]
    return peripherals[(peripherals.index(name) + 1) % len(peripherals)]


async def ble_task(device_name, led):
    dst = next_peripheral(device_name)
    print(f"Peripheral {device_name} active, sends to {dst}")
    # Random start: after a reset, the relays would ignore a restart from 0
    # until it caught up with the last number they saw.
    seq = random.getrandbits(8)
    last_seq = {}

    while True:
        # === Send the local distance ===
        distance = DISTANCE.read()
        seq = (seq + 1) % 256
        try:
            await aioble.advertise(
                interval_us=100_000,
                adv_data=encode(device_name, device_name, dst, seq, 0, distance),
                connectable=False,
                timeout_ms=ADV_MS,
            )
        except asyncio.TimeoutError:
            pass  # Normal end of a non-connectable advertisement
        print(f"{device_name} sent {distance} mm to {dst} (seq {seq})")

        # === Receive the messages addressed to this peripheral ===
        async with aioble.scan(SCAN_MS, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                name = result.name()
                if not name or not name.startswith("STeaMi-R"):
                    continue
                message = decode(result.adv_data)
                if not message:
                    continue
                src, msg_dst, msg_seq, hop, value = message
                if msg_dst != device_name or not is_new(last_seq, src, msg_seq):
                    continue
                if value < THRESHOLD_MM:
                    led.on()
                else:
                    led.off()
                print(f"{device_name} received {value} mm from {src} via {name} ({hop} hops)")


async def display_task(name):
    while True:
        SCREEN.clear()
        # 15 characters do not fit the round screen at scale SCREEN.k: scale 1
        label = "Peripheral node"
        SCREEN.text(label, ((SCREEN.width - len(label) * 8) // 2, SCREEN.u(60)), scale=1)
        SCREEN.text(name, ((SCREEN.width - len(name) * 8 * SCREEN.k) // 2, SCREEN.u(70)), scale=SCREEN.k)
        SCREEN.show()
        await asyncio.sleep(0.5)


async def run(device_name, led):
    await asyncio.gather(ble_task(device_name, led), display_task(device_name))
