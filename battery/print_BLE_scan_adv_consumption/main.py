from pins import *   # BATTERY.current(), SCREEN (begin() avant les imports BLE : il alloue 40 Ko)
import bluetooth
import uasyncio as asyncio
import aioble
import struct
import urandom
from time import ticks_ms

# === Initialisation BLE ===
ble = bluetooth.BLE()
ble.active(True)

mac_bytes = ble.config('mac')[1]
mac_suffix = ''.join(f'{b:02X}' for b in mac_bytes[-2:])
device_name = f"STeaMi-{mac_suffix}"
print("Device name:", device_name)

# === Paramètres ===
SCAN_DURATION = 20    # secondes
ADV_TIMEOUT = 5000    # ms
N_MEASURES = 10       # nombre de mesures pour la moyenne

devices_distances = {}

def measure_average(n=N_MEASURES, action_before=None, action_after=None):
    values = []
    if action_before:
        action_before()
        asyncio.sleep(2)

    for _ in range(n):
        val = BATTERY.current()
        values.append(val)
        sleep(0.5)

    if action_after:
        action_after()

    return sum(values) / len(values) if values else 0

# --- Fonctions auxiliaires BLE ---
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

# --- Tâche BLE avec données random ---
async def ble_task():
    while True:
        print("BLE Task: Starting scan...")

        # --- Mesure consommation témoin ---
        SCREEN.clear()
        show_lines(["Mesure en", "cours ..."])
        SCREEN.show()
        curr_baseline = measure_average()
        print(f"[Conso TEMOIN] {curr_baseline:.2f} mA")

        # Mesure consommation en réception (scan)
        def start_scan(): print(">> SCAN start")
        def stop_scan(): print(">> SCAN stop")
        curr_scan = measure_average(action_before=start_scan, action_after=stop_scan)

        async with aioble.scan(SCAN_DURATION*1000, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                name = result.name()
                if name and name.startswith("STeaMi") and name != device_name:
                    man_data = extract_manufacturer_data(result.adv_data)
                    if man_data and len(man_data) == 2:
                        distance, = struct.unpack("h", man_data)
                        devices_distances[name] = (distance, ticks_ms())
                        print(f"Received from {name}: {distance}")

        print(f"[Conso SCAN] {curr_scan:.2f} mA soit {curr_scan - curr_baseline:.2f} mA d'ecrat du temoin")
        await asyncio.sleep(1)

        # Mesure consommation en émission (advertising)
        def start_adv(): print(">> ADV start")
        def stop_adv(): print(">> ADV stop")
        curr_adv = measure_average(action_before=start_adv, action_after=stop_adv)

        # Générer une donnée random à envoyer (entre 0 et 100)
        random_data = urandom.getrandbits(8) % 101  # 0 à 100
        man_data = struct.pack("h", random_data)
        adv_payload = advertising_payload(name=device_name, manufacturer_data=man_data)

        try:
            await aioble.advertise(
                interval_us=150_000,
                adv_data=adv_payload,
                connectable=False,
                timeout_ms=ADV_TIMEOUT
            )
            print(f"Advertisement done. Sent random value: {random_data}")
        except asyncio.TimeoutError:
            print("Advertisement timeout (non-connectable).")

        print(f"[Conso ADV] {curr_adv:.2f} mA soit {curr_adv - curr_baseline:.2f} mA d'ecrat du temoin")
        await asyncio.sleep(2)

        # Affichage des consommations
        SCREEN.clear()
        show_lines([
            f"{device_name}",
            f"T : {curr_baseline:.2f} mA",
            f"S : {curr_scan:.2f} mA",
            f"A : {curr_adv:.2f} mA",
        ])
        SCREEN.show()

        await asyncio.sleep(5) # Pause avant la prochaine itération

        SCREEN.clear() # Effacer l'écran
        SCREEN.show() # Mettre à jour l'affichage

# --- Main ---
async def main():
    await asyncio.gather(
        ble_task()
    )

asyncio.run(main())
