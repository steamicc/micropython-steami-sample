"""BLE reference: the board compares its temperature and humidity with those
of a Xiaomi LYWSD03MMC thermo-hygrometer (pvvx firmware) placed next to it.

The screen shows both readings and their difference. A CSV line goes to the
serial console every CSV_PERIOD seconds, to keep a record of the test.

Sensor choice: an empty TARGET follows the nearest Xiaomi (best RSSI heard in
the last FORGET seconds); otherwise a MAC address ("A4:C1:38:...") or a BLE
name.
"""

import asyncio
import math
import time

import aioble
from steami import Humidity, Screen, Temperature
from steami_screen import DARK, GRAY, WHITE
from xiaomi_ble import decode, humidity_at

TARGET = ""        # "": the nearest one; otherwise a MAC address or a BLE name
FORGET = 30        # s: a sensor silent for longer is no longer chosen
CSV_PERIOD = 5     # s
MAX_SENSORS = 20   # bounds the memory when many sensors are in range
HYSTERESIS = 6     # dB: another sensor must be clearly stronger to replace the followed one

# The screen first: its frame is allocated by begin(), before the heap fragments.
SCREEN = Screen()
SCREEN.begin()

temperature = Temperature()
humidity = Humidity()
temperature.begin()
humidity.begin()

sensors = {}     # address -> {"name", "rssi", "seen", "m"}
followed = None  # address of the displayed sensor
start = time.ticks_ms()


def now():
    return time.ticks_diff(time.ticks_ms(), start) // 1000


def remember(address, name, rssi, m):
    if address not in sensors and len(sensors) >= MAX_SENSORS:
        oldest = min(sensors, key=lambda a: sensors[a]["seen"])
        del sensors[oldest]
    new = address not in sensors
    s = sensors.setdefault(address, {"name": "", "rssi": rssi, "seen": 0, "m": None})
    if name:
        s["name"] = name
    s["rssi"], s["seen"], s["m"] = rssi, now(), m
    if new:
        print("# sensor", address, name or "?", m["format"], rssi, "dBm")


def choose():
    global followed
    alive = [a for a in sensors
             if now() - sensors[a]["seen"] <= FORGET and sensors[a]["m"].get("temperature") is not None]
    if TARGET:
        target = TARGET.upper()
        for a in alive:
            if a == target or sensors[a]["name"].upper() == target:
                return a
        return None
    if not alive:
        return None
    best = max(alive, key=lambda a: sensors[a]["rssi"])
    # two sensors side by side have almost the same RSSI: keep the followed one
    if followed not in alive or sensors[best]["rssi"] >= sensors[followed]["rssi"] + HYSTERESIS:
        followed = best
    return followed


async def scanner():
    while True:
        # active scan: the scan response carries the BLE name
        async with aioble.scan(1500, interval_us=30000, window_us=30000, active=True) as results:
            async for r in results:
                m = decode(r.adv_data) or decode(r.resp_data)
                if m is None:
                    continue
                address = m.get("mac") or r.device.addr_hex().upper()
                if m["format"] == "mibeacon":
                    if address not in sensors:
                        print("# original Xiaomi firmware (encrypted, unreadable):", address)
                        sensors[address] = {"name": "", "rssi": r.rssi, "seen": now(), "m": m}
                    continue
                remember(address, r.name(), r.rssi, m)
        await asyncio.sleep_ms(100)


def line(s, y, color=WHITE):
    # centred: a cell is 8 px wide on 128 px, 16 px (Spleen 8x16 x 2) on 240 px
    width = len(s) * 8 * SCREEN.k
    SCREEN.text(s, ((SCREEN.width - width) // 2, SCREEN.u(y)), color)


def reading(t, h):
    st = "--.-C" if t is None or math.isnan(t) else f"{t:.1f}C"
    sh = "--%" if h is None or math.isnan(h) else f"{h:.1f}%"
    return st + " " + sh


def number(v):
    return "" if v is None or math.isnan(v) else f"{v:.2f}"


def difference(a, b, fmt):
    if a is None or b is None or math.isnan(a) or math.isnan(b):
        return "--"
    return fmt.format(a - b)


async def display():
    last_csv = -CSV_PERIOD
    print("t_s;address;rssi;format;T_ref;RH_ref;T_board;RH_board;RH_ref_at_T_board")
    while True:
        t_board, h_board = temperature.read(), humidity.read()
        a = choose()
        SCREEN.clear()
        SCREEN.title("BLE reference")
        line("Board", 30, GRAY)
        line(reading(t_board, h_board), 39)
        if a is None:
            line("Xiaomi ?", 60, GRAY)
            line("scanning...", 70, DARK)
        else:
            s = sensors[a]
            m = s["m"]
            t_ref, h_ref = m.get("temperature"), m.get("humidity")
            # the board warms up: its humidity is compared with the reference
            # air brought to the board temperature (Tb)
            h_at = humidity_at(t_ref, h_ref, t_board)
            line(s["name"] or a[-8:], 52, GRAY)
            line(reading(t_ref, h_ref), 61)
            line("RH at Tb " + ("--%" if h_at is None else f"{h_at:.1f}%"), 70, GRAY)
            line("Difference", 82, GRAY)
            line(difference(t_board, t_ref, "{:+.1f}C") + " " + difference(h_board, h_at, "{:+.1f}%"), 91)
            line("{}dB {}s".format(s["rssi"], now() - s["seen"]), 104, DARK)
            if now() - last_csv >= CSV_PERIOD:
                last_csv = now()
                print(";".join((str(now()), a, str(s["rssi"]), m["format"],
                                number(t_ref), number(h_ref), number(t_board), number(h_board),
                                number(h_at))))
        SCREEN.show()
        await asyncio.sleep(1)


async def main():
    await asyncio.gather(asyncio.create_task(scanner()), asyncio.create_task(display()))


asyncio.run(main())
