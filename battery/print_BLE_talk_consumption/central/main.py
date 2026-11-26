from micropython import const
import asyncio
import aioble
import bluetooth
import struct
import time

from pins import *

# UUIDs
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_DEVICE_NAME_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")

# Identité du central basée sur son MAC
ble = bluetooth.BLE()
ble.active(True)
mac_bytes = ble.config('mac')[1]
mac_suffix = ''.join(f'{b:02X}' for b in mac_bytes[-2:])
device_name = f"Client-{mac_suffix}"
print("Central device name:", device_name)

# Globales
discovered_devices = []
selected_index = 0
scan_active = True
active_connection = None

# Mesure de la consommation moyenne
async def measure_average(duration_s=1, label=""):
    values = []
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_s * 1000:
        val = fg.current_average()
        values.append(val)
        await asyncio.sleep(0.25)
    avg = sum(values) / len(values) if values else 0
    print(f"[{label}] Moyenne {avg:.2f} mA")
    return avg

# Affichage
async def display_task():
    global selected_index, discovered_devices
    while True:
        if scan_active:
            display.fill(0)
            display.text(device_name, text_x_center_position(device_name), 25, 255)
            display_menu(discovered_devices, selected_index)
            display.show()
        await asyncio.sleep(0.1)

# Boutons
async def button_task():
    global selected_index, discovered_devices, scan_active, active_connection
    while True:
        button = await wait_for_button()
        if button == "A" and discovered_devices:
            selected_index = (selected_index + 1) % len(discovered_devices)
        elif button == "B" and discovered_devices:
            selected_index = (selected_index - 1) % len(discovered_devices)
        elif button == "MENU":
            if scan_active:
                if not discovered_devices:
                    print("No devices found.")
                    continue
                scan_active = False
                selected = discovered_devices[selected_index]
                print(f"Connecting to {selected.name()} @ {selected.device.addr_hex()}")
                asyncio.create_task(connect_to_device(selected.device, selected.name()))
            else:
                if active_connection:
                    print("Disconnecting...")
                    await active_connection.disconnect()
                    active_connection = None
                scan_active = True
        await asyncio.sleep(0.1)

# Connexion + envoi du nom
async def connect_to_device(device, name):
    global active_connection, scan_active

    try:
        task_measure = asyncio.create_task(measure_average(5,"Connexion"))
        connection = await device.connect(timeout_ms=5000)
        active_connection = connection
    except asyncio.TimeoutError:
        print("Connection timeout")
        scan_active = True
        return

    async with connection:
        try:
            service = await connection.service(_ENV_SENSE_UUID)
            temp_char = await service.characteristic(_ENV_SENSE_TEMP_UUID)
            name_char = await service.characteristic(_DEVICE_NAME_UUID)

            # 🔽 Écrire notre nom dans la caractéristique
            await name_char.write(device_name.encode())
            print("Nom envoye :", device_name)

        except Exception as e:
            print("Service discovery failed:", e)
            scan_active = True
            return

        while connection.is_connected() and not scan_active:
            try:
                task_measure = asyncio.create_task(measure_average(1,"Connecte"))
                raw = await temp_char.read()
                distance_mm = struct.unpack("<h", raw)[0]
                print("Distance:", distance_mm)

                display.fill(0)
                display.text(name, text_x_center_position(name), 25, 255)
                display.text(f"{distance_mm} mm", text_x_center_position(f"{distance_mm} mm"), 60, 255)
                display.show()
            except Exception as e:
                print("Read error:", e)
                break

            await asyncio.sleep(1)

        print("Disconnected")
        active_connection = None
        scan_active = True

# Scan
async def scan_task():
    global discovered_devices
    while True:
        if scan_active:
            print("--- Scanning ---")
            task_measure = asyncio.create_task(measure_average(1,"Scan"))
            devices = []
            async with aioble.scan(1000, interval_us=30000, window_us=30000, active=True) as scanner:
                async for result in scanner:
                    name = result.name()
                    if name and name.startswith("STeaMi"):
                        if result.device not in [d.device for d in devices]:
                            print(f"Found: {name}")
                            devices.append(result)
            discovered_devices = devices
        await asyncio.sleep(0.1)

# Main
async def main():
    await asyncio.gather(
        scan_task(),
        display_task(),
        button_task()
    )

asyncio.run(main())