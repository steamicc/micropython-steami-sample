import bluetooth, uasyncio as asyncio, aioble, struct, json
from time import ticks_ms
from pins import *

KEY = 0x5A  # Clé XOR simple

def xor_encrypt(data: bytes) -> bytes:
    return bytes([b ^ KEY for b in data])

def advertising_payload(name=None, manufacturer_data=None):
    payload = bytearray()
    if name:
        name_bytes = name.encode()
        payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes
    if manufacturer_data:
        payload += bytes((len(manufacturer_data) + 1, 0xFF)) + manufacturer_data
    return payload

def extract_manufacturer_data(adv_bytes):
    i = 0
    while i < len(adv_bytes):
        length = adv_bytes[i]
        if length == 0: break
        type_ = adv_bytes[i + 1]
        if type_ == 0xFF:
            return adv_bytes[i + 2 : i + 1 + length]
        i += 1 + length
    return None

async def ble_task(device_name):
    seen_msgs = set()
    ble = bluetooth.BLE(); ble.active(True)
    print(f"Relay {device_name} active")

    while True:
        async with aioble.scan(800, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                name = result.name()
                if not name or name == device_name or not name.startswith("STeaMi"): continue
                man = extract_manufacturer_data(result.adv_data)
                if not man: continue
                try:
                    msg_json = xor_encrypt(man).decode()
                    msg = json.loads(msg_json)
                except Exception:
                    continue
                msg_id = (msg["src"], msg["dst"], msg["payload"])
                if msg_id in seen_msgs: continue
                seen_msgs.add(msg_id)
                print(f"{device_name} relays: {msg}")
                msg["hop"] += 1
                man_data = xor_encrypt(json.dumps(msg).encode())
                adv = advertising_payload(name=device_name, manufacturer_data=man_data)
                try:
                    await aioble.advertise(interval_us=150_000, adv_data=adv, connectable=False, timeout_ms=500)
                except:
                    pass
        await asyncio.sleep_ms(200)

async def display_task(name):
    while True:
        display.fill(0)
        display.text(name, 10, 20, 255)
        display.text("Relay mesh node", 10, 35, 255)
        display.show()
        await asyncio.sleep(0.5)

async def run(device_name):
    await asyncio.gather(ble_task(device_name), display_task(device_name))