"""BLE RSSI room mapper example using aioble, OLED screen and DAPLink flash.

One board acts as scanner while 2-3 other boards act as beacons.
The user moves around the room with the scanner and presses RIGHT to
record RSSI measurements at each position. Data is saved as CSV via
DAPLink flash.

Roles (single file):
    - Navigate menu with UP/DOWN, confirm with RIGHT
    - BEACON mode: select beacon ID and advertise continuously, LEFT to exit
    - SCANNER mode: scan beacons, record RSSI points, save to CSV

Beacon naming convention:
    Beacon_M1, Beacon_M2, Beacon_M3

CSV format:
    point_id,beacon_name,rssi

Hardware:
    - 3-4 STeaMi boards (2-3 beacons + 1 scanner)
    - OLED/LCD screen (SSD1327 on V1a/V1b, GC9A01 on V1c) + D-PAD + DAPLink flash on scanner board

Learning goals:
    - Experimental data collection methodology
    - Understanding RSSI variability
    - File I/O via DAPLink flash
    - Introduction to radio fingerprinting
"""

import uasyncio as asyncio
from time import sleep_ms, ticks_diff, ticks_ms

import aioble
from daplink_bridge import DaplinkBridge
from daplink_flash import DaplinkFlash
from machine import I2C, Pin
from mcp23009e import MCP23009E
from mcp23009e.const import (
    MCP23009_BTN_DOWN,
    MCP23009_BTN_LEFT,
    MCP23009_BTN_RIGHT,
    MCP23009_BTN_UP,
    MCP23009_DIR_INPUT,
    MCP23009_I2C_ADDR,
    MCP23009_LOGIC_LOW,
    MCP23009_PULLUP,
)
from steami import Screen
from steami_screen import LIGHT

# === Display ===
# begin() first: the frame buffer needs a large block of RAM.
screen = Screen()
screen.begin()

# === Beacon names ===
BEACON_NAMES = ["Beacon_M1", "Beacon_M2", "Beacon_M3"]

# === RSSI calibration offsets (dB, specific to your boards) ===
# Two boards at the same distance may not report the same RSSI. To
# compare the beacons, put the scanner against each beacon in turn, note
# the RSSI shown, and add the offset that brings them to the same value.
RSSI_OFFSET = {
    "Beacon_M1": 0,
    "Beacon_M2": 0,
    "Beacon_M3": 0,
}

# A beacon not heard for this long is shown as "---" and not recorded.
RSSI_MAX_AGE_MS = 3000

# === Buttons ===
i2c = I2C(1)
reset_expander = Pin("RST_EXPANDER", Pin.OUT)
mcp = MCP23009E(i2c, address=MCP23009_I2C_ADDR, reset_pin=reset_expander)
for btn in [MCP23009_BTN_UP, MCP23009_BTN_DOWN, MCP23009_BTN_RIGHT, MCP23009_BTN_LEFT]:
    mcp.setup(btn, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)

# === DAPLink flash ===
bridge = DaplinkBridge(i2c)
flash = DaplinkFlash(bridge)

# === BLE parameters ===
ADV_INTERVAL_US = 50_000
ADV_TIMEOUT_MS = 100
SCAN_DURATION_MS = 500

# === Shared state ===
current_rssi = {}
point_id = 0
stop_flag = False


# =============================================================================
# === HELPERS =================================================================
# =============================================================================


def build_adv_payload(name):
    """Build a minimal BLE advertising payload with device name."""
    payload = bytearray()
    name_bytes = name.encode()
    payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes
    return payload


def is_pressed(btn):
    """Return True if button is currently pressed."""
    return mcp.get_level(btn) == MCP23009_LOGIC_LOW


def wait_released(btn):
    """Wait until button is released."""
    while is_pressed(btn):
        sleep_ms(20)


async def wait_released_async(btn):
    """Wait until button is released, letting the other tasks run."""
    while is_pressed(btn):
        await asyncio.sleep_ms(20)


def fresh_rssi():
    """Return {beacon_name: rssi} for the beacons heard recently."""
    now = ticks_ms()
    return {
        name: rssi
        for name, (rssi, seen_at) in current_rssi.items()
        if ticks_diff(now, seen_at) < RSSI_MAX_AGE_MS
    }


def menu_select(title, items):
    """Generic D-PAD menu. Returns selected index."""
    selected = 0
    while True:
        screen.clear()
        screen.title(title)
        screen.menu(items, selected=selected)
        screen.subtitle("UP/DOWN: nav", "RIGHT: OK")
        screen.show()

        sleep_ms(150)
        if is_pressed(MCP23009_BTN_UP):
            wait_released(MCP23009_BTN_UP)
            selected = (selected - 1) % len(items)
        elif is_pressed(MCP23009_BTN_DOWN):
            wait_released(MCP23009_BTN_DOWN)
            selected = (selected + 1) % len(items)
        elif is_pressed(MCP23009_BTN_RIGHT):
            wait_released(MCP23009_BTN_RIGHT)
            return selected


# =============================================================================
# === BEACON MODE =============================================================
# =============================================================================


async def beacon_ble_task(beacon_name):
    """Advertise as Beacon_Mx until stop_flag is set."""
    adv_payload = build_adv_payload(beacon_name)
    print(f"Beacon mode: advertising as {beacon_name}")
    while not stop_flag:
        try:
            await aioble.advertise(
                interval_us=ADV_INTERVAL_US,
                adv_data=adv_payload,
                connectable=False,
                timeout_ms=ADV_TIMEOUT_MS,
            )
        except asyncio.TimeoutError:
            pass


async def beacon_display_task(beacon_name):
    """Show beacon status on OLED until stop_flag is set."""
    while not stop_flag:
        screen.clear()
        screen.title("BEACON")
        screen.subtitle(beacon_name, "Broadcasting", "LEFT: menu")
        screen.show()
        await asyncio.sleep_ms(1000)


async def beacon_button_task():
    """Watch for LEFT button to exit beacon mode."""
    global stop_flag
    while not stop_flag:
        if is_pressed(MCP23009_BTN_LEFT):
            await wait_released_async(MCP23009_BTN_LEFT)
            stop_flag = True
            return
        await asyncio.sleep_ms(100)


async def run_beacon(beacon_name):
    """Run beacon mode until LEFT is pressed."""
    await asyncio.gather(
        beacon_ble_task(beacon_name),
        beacon_display_task(beacon_name),
        beacon_button_task(),
    )


# =============================================================================
# === SCANNER MODE ============================================================
# =============================================================================


async def scanner_ble_task():
    """Scan for all beacons and update current RSSI with calibration offset."""
    global current_rssi
    while not stop_flag:
        async with aioble.scan(
            SCAN_DURATION_MS,
            interval_us=10000,
            window_us=10000,
            active=True,
        ) as scanner:
            async for result in scanner:
                name = result.name()
                if name in BEACON_NAMES:
                    rssi = result.rssi + RSSI_OFFSET.get(name, 0)
                    current_rssi[name] = (rssi, ticks_ms())


async def scanner_display_task():
    """Display beacons RSSI, handle recording and stop."""
    global point_id, stop_flag

    while not stop_flag:
        if is_pressed(MCP23009_BTN_RIGHT):
            await wait_released_async(MCP23009_BTN_RIGHT)
            measures = fresh_rssi()
            if measures:
                point_id += 1
                for name, rssi in measures.items():
                    line = f"{point_id},{name},{rssi}"
                    flash.write_line(line)
                    print(line)

                screen.clear()
                screen.title(f"Point {point_id} OK")
                screen.subtitle(
                    f"{len(measures)} beacons",
                    "RIGHT: next",
                    "LEFT: stop",
                )
                screen.show()
                await asyncio.sleep_ms(800)

        elif is_pressed(MCP23009_BTN_LEFT):
            await wait_released_async(MCP23009_BTN_LEFT)
            stop_flag = True
            break

        else:
            screen.clear()
            screen.title("ROOM MAPPER")

            measures = fresh_rssi()
            cx, cy = screen.center
            k = screen.k
            y = screen.u(38)
            for name in BEACON_NAMES:
                rssi = measures.get(name, "---")
                short = name[-2:]
                label = f"{short}: {rssi} dBm"
                x = cx - len(label) * 4 * k
                screen.text(label, (x, y), LIGHT, scale=k)
                y += screen.u(14)

            screen.subtitle(f"#{point_id}", "R:rec L:stop")
            screen.show()

        await asyncio.sleep_ms(200)


async def run_scanner():
    """Run scanner mode until stop_flag is set."""
    await asyncio.gather(
        scanner_ble_task(),
        scanner_display_task(),
    )


# =============================================================================
# === MAIN LOOP ===============================================================
# =============================================================================

while True:
    # Reset state
    current_rssi = {}
    point_id = 0
    stop_flag = False

    # Main mode selection menu
    mode_idx = menu_select("SELECT MODE", ["SCANNER", "BEACON"])

    if mode_idx == 1:
        # Beacon mode — select beacon ID
        beacon_idx = menu_select("PICK BEACON", BEACON_NAMES)
        beacon_name = BEACON_NAMES[beacon_idx]

        screen.clear()
        screen.title("BEACON")
        screen.subtitle(beacon_name, "Starting...")
        screen.show()
        sleep_ms(500)

        asyncio.run(run_beacon(beacon_name))

        # Back to menu after LEFT pressed
        screen.clear()
        screen.title("STOPPED")
        screen.subtitle("Back to menu")
        screen.show()
        sleep_ms(1000)

    else:
        # Scanner mode
        flash.set_filename("RSSI_MAP", "CSV")
        flash.clear_flash()
        flash.write_line("point_id,beacon_name,rssi")

        screen.clear()
        screen.title("ROOM MAPPER")
        screen.subtitle("RIGHT: record", "LEFT: stop")
        screen.show()
        sleep_ms(500)

        asyncio.run(run_scanner())

        # Show summary then loop back to menu
        screen.clear()
        screen.title("SAVED!")
        screen.subtitle(
            f"{point_id} points",
            "RSSI_MAP.CSV",
            "RIGHT: menu",
        )
        screen.show()

        while not is_pressed(MCP23009_BTN_RIGHT):
            sleep_ms(100)
        wait_released(MCP23009_BTN_RIGHT)
