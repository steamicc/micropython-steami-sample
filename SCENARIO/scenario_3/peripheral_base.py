import bluetooth, uasyncio as asyncio, aioble, struct, json
from time import ticks_ms
from pins import *

KEY = 0x5A

ble = bluetooth.BLE()
ble.active(True)
local_distance = 0

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

async def ble_task(device_name, relay_name, led):
    print(f"Peripheral {device_name} active, linked to {relay_name}")

    while True:
        # === Lecture capteur + envoi ===
        local_distance = DISTANCE.read()
        msg = {"src": device_name, "dst": relay_name, "payload": local_distance, "hop": 0}
        man_data = xor_encrypt(json.dumps(msg).encode())
        adv = advertising_payload(name=device_name, manufacturer_data=man_data)
        try :
            await aioble.advertise(
                interval_us=150_000, 
                adv_data=adv, 
                connectable=False, 
                timeout_ms=500)
            print("Advertisement done.")
        except asyncio.TimeoutError:
            print("Advertisement timeout (non-connectable).")

        # === Réception éventuelle ===
        async with aioble.scan(500, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                name = result.name()
                if not name or not name.startswith("STeaMi-R"): continue
                man = extract_manufacturer_data(result.adv_data)
                if not man: continue
                try:
                    msg_json = xor_encrypt(man).decode()
                    msg = json.loads(msg_json)
                except:
                    continue
                if msg.get("dst") == device_name:
                    distance = msg.get("payload", 0)
                    if distance < 300:
                        led.on()
                    else:
                        led.off()
                    print(f"{device_name} received {distance} from {name}")
        await asyncio.sleep_ms(500)

async def display_task(name):
    while True:
        display.fill(0)
        display.text("Peripheral node", 10, 60, 255)
        display.text(name, 10, 70, 255)
        display.show()
        await asyncio.sleep(0.5)

async def run(device_name, relay_name, led):
    print("Peripheral base")
    print(f"Device: {device_name}, Relay: {relay_name}, LED: {led}")
    print("Starting tasks...")
    await asyncio.gather(ble_task(device_name, relay_name, led), display_task(device_name))
