import bluetooth
import uasyncio as asyncio
import aioble
import struct
from time import ticks_ms
from pins import *  # contient LED_RED, LED_GREEN, LED_BLUE, display, fg

# === Initialisation BLE ===
ble = bluetooth.BLE()
ble.active(True)

device_name = "STeaMi-R2"
print("Device name:", device_name)

# === Paramètres ===
SCAN_DURATION = 500
ADV_TIMEOUT = 500

# === Données globales ===
devices_distances = {}   # {device_name: (distance, last_seen_ms)}
forwarded_presence = None
energy_value = 0.0       # Valeur mesurée de consommation énergétique

# === Fonctions auxiliaires ===
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
        if length == 0:
            break
        type_ = adv_bytes[i + 1]
        if type_ == 0xFF:
            return adv_bytes[i + 2 : i + 1 + length]
        i += 1 + length
    return None

def text_x_center(text):
    return max((128 - len(text) * 8) // 2, 0)

# === Tâche BLE principale ===
async def ble_task():
    global forwarded_presence
    while True:
        print("BLE Task: Scanning...")
        async with aioble.scan(SCAN_DURATION, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                name = result.name()
                if name and name.startswith("STeaMi") and name != device_name:
                    man_data = extract_manufacturer_data(result.adv_data)
                    if man_data and len(man_data) == 2:
                        distance, = struct.unpack("h", man_data)
                        devices_distances[name] = (distance, ticks_ms())
                        print(f"Received from {name}: {distance} cm")
                    if man_data and len(man_data) == 1 and name.startswith("STeaMi-R"):
                        forwarded_presence, = struct.unpack("b", man_data)
                        devices_distances[name] = (forwarded_presence, ticks_ms())
                        print(f"Received presence from {name}: {forwarded_presence}")

        # === Phase d’annonce ===
        await asyncio.sleep_ms(SCAN_DURATION + 50)

        if forwarded_presence is not None:
            print(f"{device_name} advertising presence: {forwarded_presence}")

            # Indicateur lumineux selon la présence
            if forwarded_presence == 0:
                man_data = struct.pack("b", 0)
                LED_RED.on()
            elif forwarded_presence == 1:
                man_data = struct.pack("b", 1)
                LED_GREEN.on()
            else:
                man_data = struct.pack("b", 2)
                LED_BLUE.on()

            adv_payload = advertising_payload(name=device_name, manufacturer_data=man_data)

            try:
                await aioble.advertise(
                    interval_us=150_000,
                    adv_data=adv_payload,
                    connectable=False,
                    timeout_ms=ADV_TIMEOUT,
                )
                print("Advertisement done.")
            except asyncio.TimeoutError:
                print("Advertisement timeout.")
            finally:
                LED_RED.off()
                LED_GREEN.off()
                LED_BLUE.off()
                forwarded_presence = None

        await asyncio.sleep_ms(200)

# === Tâche d’affichage ===
async def display_task():
    global energy_value
    while True:
        # Lecture de la consommation énergétique
        try:
            energy_value = fg.current_average()
        except Exception as e:
            print("Erreur lecture énergie :", e)
            energy_value = 0.0

        display.fill(0)
        display.text(device_name, text_x_center(device_name), 10, 255)

        # Afficher la consommation d'énergie
        display.text(f"E:{energy_value:.2f} mA", text_x_center("E:000.00 mA"), 25, 255)

        # Appareils récemment vus
        recent_devices = sorted(
            devices_distances.items(),
            key=lambda item: item[1][1],
            reverse=True
        )[:4]

        y = 45
        for name, (dist, _) in recent_devices:
            display.text(f"{name[-4:]}: {dist}", text_x_center("XXXX: XXX"), y, 255)
            y += 10

        display.show()
        await asyncio.sleep(0.5)

# === Programme principal ===
async def main():
    await asyncio.gather(ble_task(), display_task())

asyncio.run(main())
