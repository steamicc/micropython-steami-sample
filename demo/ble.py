import aioble
import uasyncio as asyncio
import bluetooth
from aioble import peripheral

from pins import *
from advertizing import *

ble = bluetooth.BLE()
ble.active(True)
aioble.config(gap_name="STeaMi")

ble = ["RECEIVE", "EMIT", "EXIT"]

async def run_ble(ble_index):
    if ble_index == 0:
        print("BLE RECEIVE")
        SCREEN.clear()
        SCREEN.text("BLE SCAN ... ", "CENTER", WHITE)
        SCREEN.show()
        results = await ble_receive()
        await display_receive(results)
    elif ble_index == 1:
        print("BLE EMIT")
        await run_ble_adv()
        await asyncio.sleep(0.2)
    elif ble_index == 2:
        return

async def ble_menu():
    print("--- BLE ---")

    ble_index = 0
    display_menu("BLE", ble, ble_index)

    while True:
        btn = await wait_for_button()
        if btn == "A":
            ble_index -= 1
        elif btn == "B":
            ble_index += 1
        elif btn == "MENU":
            if ble[ble_index] == "EXIT":
                break
            await run_ble(ble_index)
        if ble_index >= len(ble) :
            ble_index = 0
        elif ble_index < 0 :
            ble_index = len(ble) - 1
        display_menu("BLE", ble, ble_index)

async def ble_receive():
    print("START BLE SCAN")
    results = []
    async with aioble.scan(1000, interval_us=30000, window_us=30000) as scanner:
        async for result in scanner:
            results.append(result)

    print("END BLE SCAN")
    # Remove duplicate MAC addresses
    unique_results = []
    seen_addresses = set()
    for result in results:
        mac_address = tuple(result.device.addr)
        if mac_address not in seen_addresses:
            seen_addresses.add(mac_address)
            unique_results.append(result)
    results = unique_results
    return results

async def display_receive(results):
    print("BLE SCAN RESULTS")

    result_index = 0
    while True:
        print(f"{result_index+1}/{len(results)}: {results[result_index]}")

        SCREEN.clear()
        SCREEN.title("RESULTS", WHITE)
        if not results:
            print("Aucun résultat à afficher.")
            display_line("No results", 50)
            return
        else :
            display_line(f"{result_index+1}/{len(results)}", 32)
            mac_address = ''.join(['%02x' % b for b in results[result_index].device.addr]).upper()
            display_line("MAC address:", 44)
            display_line(f"{mac_address}", 54)
            display_line(f"RSSI : {results[result_index].rssi}", 70)
            display_line(f"Name : {results[result_index].name()}", 82)

        SCREEN.show()

        btn = await wait_for_button()
        if btn == "A":
            result_index -= 1
        elif btn == "B":
            result_index += 1
        elif btn == "MENU":
            break
        if result_index >= len(results) :
            result_index = 0
        elif result_index < 0 :
            result_index = len(results) - 1

def make_payload(name="STeaMi"):
    name_bytes = name.encode()
    payload = bytearray()
    payload += bytes((2, 0x01, 0x06))  # Flags
    payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes  # Complete local name
    return payload

async def ble_emit():
    print("BLE EMIT")
    print("A to SEND | MENU to EXIT")
    iteration = 0
    peripheral()
    while True:
        btn = await wait_for_button()

        if btn == "A":
            print(f"[{iteration}] Advertising...")
            try:
                await aioble.advertise(
                    interval_us=300_000,
                    adv_data=make_payload(),
                    timeout_ms=10000
                )
                print("Advertising done")
            except Exception as e:
                print("Advertising failed:", repr(e))
            iteration += 1

        elif btn == "MENU":
            print("Exiting BLE EMIT.")
            break

        print("A to SEND | MENU to EXIT")
