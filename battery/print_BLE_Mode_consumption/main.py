from pins import *   # pour fg.current_average() et display si dispo

import bluetooth, aioble, uasyncio as asyncio
import machine, urandom, struct

# ==========================
# CONFIGURATION
# ==========================
N_MEASURES = 10  # nombre de mesures par scénario

# --- Fonction de mesure ---
def measure_average(n=N_MEASURES, action_before=None, action_after=None):
    values = []
    if action_before:
        action_before()
        sleep(1)  # stabilisation
    
    for _ in range(n):
        val = fg.current_average()   # ton instrument de mesure
        values.append(val)
        sleep(0.5)
    
    if action_after:
        action_after()
    
    return sum(values) / len(values) if values else 0

async def adv_fast():
    print(">> Advertising rapide (100ms interval)")
    adv_payload = aioble.advertising_payload(
        name="STM32WB55_FAST",
        manufacturer_data=struct.pack("h", urandom.getrandbits(8))
    )
    await aioble.advertise(
        interval_us=100_000,   # 100 ms
        adv_data=adv_payload,
        connectable=False,
        timeout_ms=5000
    )

def start_adv_fast():
    loop = asyncio.get_event_loop()
    loop.create_task(adv_fast())

async def adv_slow():
    print(">> Advertising lent (1s interval) + lightsleep")
    adv_payload = aioble.advertising_payload(
        name="STM32WB55_SLOW",
        manufacturer_data=struct.pack("h", urandom.getrandbits(8))
    )
    await aioble.advertise(
        interval_us=1_000_000,   # 1 seconde
        adv_data=adv_payload,
        connectable=False,
        timeout_ms=5000
    )
    # mettre en sommeil pendant l’attente
    machine.lightsleep(1000)

def start_adv_slow():
    loop = asyncio.get_event_loop()
    loop.create_task(adv_slow())

# --- Fonction d'affichage sur OLED ---
def show_on_display(title, val, y):
    text = f"{title}: {val:.1f} mA"
    x = max((128 - len(text)*8)//2, 0)  # centrage
    display.text(text, x, y, 255)

while True:
    # ==========================
    # TEST 1 : Consommation témoin
    # ==========================
    def baseline_action():
        print(">> TEMOIN (repos)")

    curr_baseline = measure_average(action_before=baseline_action)
    print(f"[TEMOIN] Consommation : {curr_baseline:.2f} mA")

    # ==========================
    # TEST 2 : Advertising rapide
    # ==========================
    ble = bluetooth.BLE()
    ble.active(True)

    curr_adv_fast = measure_average(action_before=start_adv_fast)
    print(f"[ADV RAPIDE] Consommation : {curr_adv_fast:.2f} mA soit {curr_adv_fast - curr_baseline:.2f} mA d'ecart du temoin")

    # ==========================
    # TEST 3 : Advertising lent + lightsleep
    # ==========================

    curr_adv_slow = measure_average(action_before=start_adv_slow)
    print(f"[ADV LENT + SLEEP] Consommation : {curr_adv_slow:.2f} mA soit {curr_adv_slow - curr_baseline:.2f} mA d'ecart du temoin")

    # ==========================
    # Résumé affichage OLED
    # ==========================
    display.fill(0)

    show_on_display("T", curr_baseline, 50)
    show_on_display("ADV R", curr_adv_fast, 60)
    show_on_display("ADV L", curr_adv_slow, 70)

    display.show()

    # Pause avant nouvelle série de mesures
    sleep(5)
    display.fill(0)
    display.show()
    ble.active(False)