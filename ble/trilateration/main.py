"""BLE trilateration indoor positioning example using aioble and the OLED/LCD screen.

3 fixed beacon boards broadcast their identity. A mobile board scans all 3,
converts RSSI to distance using the log-distance path loss model, then
trilaterates a 2D position displayed as a dot on a live map.

Roles (single file):
    - Navigate menu with UP/DOWN, confirm with RIGHT
    - BEACON mode: select beacon ID (M1/M2/M3) and advertise continuously
    - MOBILE mode: scan all beacons, trilaterate and display live position

Path loss model (per beacon):
    d = 10 ^ ((RSSI_ref - RSSI) / (10 * n))
    RSSI_ref: RSSI measured at 1 m
    n: path loss exponent, computed from the RSSI at 1 m and 2 m:
       n = (RSSI_ref - RSSI_2m) / (10 * log10(2))

Calibration:
    Measure with the mobile board itself (it prints the averaged RSSI of
    each beacon on the serial console): another receiver, such as a
    phone, does not report the same RSSI. The values below come from
    the room where the example was written and must be measured again:

    Beacon   RSSI@1m   RSSI@2m   n
    M1       -75       -87       3.99
    M2       -75       -88       4.32
    M3       -80       -88       2.66

Beacon coordinates (cm, measured on site, to adapt to your room):
    M1 = (  0,   0)
    M2 = (420,   0)
    M3 = (330, 278)

Hardware:
    - 4 STeaMi boards (3 beacons + 1 mobile)
    - Round OLED/LCD screen on mobile board (SSD1327 128x128 on V1a/V1b,
      GC9A01 240x240 on V1c)
    - D-PAD for menu navigation
"""

import math
import uasyncio as asyncio
from time import sleep_ms, ticks_diff, ticks_ms

import aioble
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
from steami_screen import DARK, GRAY, LIGHT, WHITE

# === Display ===
# begin() first: the frame buffer needs a large block of RAM.
screen = Screen()
screen.begin()

# === Beacon names ===
BEACON_NAMES = ["Beacon_M1", "Beacon_M2", "Beacon_M3"]

# === Beacon coordinates in cm (measured on site) ===
BEACON_POS = {
    "Beacon_M1": (0, 0),
    "Beacon_M2": (420, 0),
    "Beacon_M3": (330, 278),
}

# === Geometric centroid of the triangle (cm) ===
CENTROID = (
    sum(x for x, _ in BEACON_POS.values()) // len(BEACON_POS),
    sum(y for _, y in BEACON_POS.values()) // len(BEACON_POS),
)

# A beacon not heard for this long is ignored.
RSSI_MAX_AGE_MS = 3000

# === Path loss calibration (measured on site) ===
# RSSI_ref: RSSI at 1 meter
RSSI_REF = {
    "Beacon_M1": -75,
    "Beacon_M2": -75,
    "Beacon_M3": -80,
}

# Path loss exponent n computed from 1m and 2m measurements:
#   n = (RSSI_ref - RSSI_2m) / (10 * log10(2))
PATH_LOSS_N = {
    "Beacon_M1": 3.99,
    "Beacon_M2": 4.32,
    "Beacon_M3": 2.66,
}

# === Distance clamping ===
MAX_DIST_CM = 430  # Slightly above the largest real distance (420cm M1-M2)

# === Trilateration validity ===
MAX_VALID_DIST_CM = 550  # Reject solutions too far from centroid

# === RSSI smoothing ===
RSSI_SAMPLES = 8

# === Position filtering ===
ALPHA = 0.15  # Exponential smoothing: 0.0=max smooth, 1.0=no filter
MIN_MOVE_CM = 15  # Ignore position changes smaller than this

# === Buttons ===
i2c = I2C(1)
reset_expander = Pin("RST_EXPANDER", Pin.OUT)
mcp = MCP23009E(i2c, address=MCP23009_I2C_ADDR, reset_pin=reset_expander)
for btn in [MCP23009_BTN_UP, MCP23009_BTN_DOWN, MCP23009_BTN_RIGHT, MCP23009_BTN_LEFT]:
    mcp.setup(btn, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)

# === BLE parameters ===
ADV_INTERVAL_US = 50_000
ADV_TIMEOUT_MS = 100
SCAN_DURATION_MS = 300

# === Shared state ===
current_rssi = {}
estimated_pos = None
filtered_pos = None
stop_flag = False
rssi_history = {name: [] for name in BEACON_NAMES}

# === Map display area (pixels) ===
# Laid out in 128 px units, scaled to the real screen size by screen.u().
MAP_X = screen.u(28)
MAP_Y = screen.u(14)
MAP_W = screen.u(72)
MAP_H = screen.u(72)

# === Real space bounding box (cm) ===
SPACE_W = 450
SPACE_H = 310


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


def rssi_to_distance(rssi, beacon_name):
    """Convert RSSI to distance in cm using per-beacon path loss model.

    Distance is clamped to MAX_DIST_CM to avoid aberrant values.
    """
    ref = RSSI_REF.get(beacon_name, -75)
    n = PATH_LOSS_N.get(beacon_name, 3.5)
    d_m = 10 ** ((ref - rssi) / (10 * n))
    return min(d_m * 100, MAX_DIST_CM)


def smooth_rssi(name, new_rssi):
    """Apply moving average to RSSI readings."""
    history = rssi_history[name]
    history.append(new_rssi)
    if len(history) > RSSI_SAMPLES:
        history.pop(0)
    return sum(history) // len(history)


def trilaterate(distances):
    """Estimate 2D position from 3 beacon distances using least-squares.

    Rejects solutions too far from the triangle centroid.

    Args:
        distances: dict {beacon_name: distance_cm}

    Returns:
        (x, y) in cm, or None if invalid.
    """
    if len(distances) < 3:
        return None

    names = list(distances.keys())
    x1, y1 = BEACON_POS[names[0]]
    x2, y2 = BEACON_POS[names[1]]
    x3, y3 = BEACON_POS[names[2]]
    r1 = distances[names[0]]
    r2 = distances[names[1]]
    r3 = distances[names[2]]

    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    D = 2 * (x3 - x1)
    E = 2 * (y3 - y1)
    F = r1**2 - r3**2 - x1**2 + x3**2 - y1**2 + y3**2

    denom = A * E - B * D
    if abs(denom) < 1e-6:
        return None

    x = (C * E - F * B) / denom
    y = (A * F - D * C) / denom

    # Reject if too far from centroid
    dx = x - CENTROID[0]
    dy = y - CENTROID[1]
    if math.sqrt(dx * dx + dy * dy) > MAX_VALID_DIST_CM:
        return None

    return (x, y)


def apply_filter(new_pos):
    """Smooth the position, then ignore moves smaller than MIN_MOVE_CM.

    The exponential moving average (filtered_pos) is updated with every
    new position. The dead band only applies to the displayed position
    (estimated_pos): a slow but steady move adds up until it exceeds
    MIN_MOVE_CM, then the dot follows.
    """
    global filtered_pos

    if filtered_pos is None:
        filtered_pos = new_pos
        return filtered_pos

    filtered_pos = (
        ALPHA * new_pos[0] + (1 - ALPHA) * filtered_pos[0],
        ALPHA * new_pos[1] + (1 - ALPHA) * filtered_pos[1],
    )

    if estimated_pos is not None:
        dx = filtered_pos[0] - estimated_pos[0]
        dy = filtered_pos[1] - estimated_pos[1]
        if math.sqrt(dx * dx + dy * dy) < MIN_MOVE_CM:
            return estimated_pos

    return filtered_pos


def world_to_screen(x, y):
    """Convert real-world cm coordinates to OLED map pixel coordinates."""
    px = MAP_X + int(x / SPACE_W * MAP_W)
    py = MAP_Y + MAP_H - int(y / SPACE_H * MAP_H)
    px = max(MAP_X, min(MAP_X + MAP_W, px))
    py = max(MAP_Y, min(MAP_Y + MAP_H, py))
    return px, py


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
# === MOBILE MODE =============================================================
# =============================================================================


async def mobile_ble_task():
    """Scan for all beacons and update smoothed RSSI."""
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
                    current_rssi[name] = (smooth_rssi(name, result.rssi), ticks_ms())


async def mobile_display_task():
    """Compute trilateration, filter position and display live map."""
    global estimated_pos, stop_flag

    loop_count = 0

    while not stop_flag:
        if is_pressed(MCP23009_BTN_LEFT):
            await wait_released_async(MCP23009_BTN_LEFT)
            stop_flag = True
            break

        # Averaged RSSI of the beacons heard recently. Printed every second
        # on the serial console, to measure RSSI_REF and PATH_LOSS_N.
        rssi = fresh_rssi()
        loop_count += 1
        if loop_count % 5 == 0:
            print("RSSI:", rssi)

        # Compute distances from smoothed RSSI
        distances = {
            name: rssi_to_distance(rssi[name], name)
            for name in BEACON_NAMES
            if name in rssi
        }

        # Trilaterate and filter
        if len(distances) == 3:
            raw_pos = trilaterate(distances)
            if raw_pos:
                estimated_pos = apply_filter(raw_pos)

        # Draw map
        screen.clear()
        screen.rect(MAP_X, MAP_Y, MAP_W, MAP_H, DARK)

        # Draw beacon markers with labels
        for name, (cx, cy) in BEACON_POS.items():
            px, py = world_to_screen(cx, cy)
            half = screen.u(3)
            screen.rect(px - half, py - half, 2 * half, 2 * half, LIGHT, fill=True)
            short = name[-2:]
            lx = px - 8 * screen.k
            ly = py - screen.u(14) if py > MAP_Y + screen.u(20) else py + screen.u(8)
            screen.text(short, (lx, ly), GRAY, scale=screen.k)

        # Draw filtered position
        if estimated_pos:
            ex = max(0, min(SPACE_W, estimated_pos[0]))
            ey = max(0, min(SPACE_H, estimated_pos[1]))
            px, py = world_to_screen(ex, ey)
            screen.circle(px, py, screen.u(3), WHITE, fill=True)

        # Distances in subtitle
        if distances:
            parts = [
                f"{name[-2:]}:{int(distances[name])}cm"
                for name in BEACON_NAMES
                if name in distances
            ]
            screen.subtitle(*parts)
        else:
            screen.subtitle("Scanning...", "LEFT: menu")

        screen.show()
        await asyncio.sleep_ms(200)


async def run_mobile():
    """Run mobile trilateration mode until LEFT is pressed."""
    await asyncio.gather(
        mobile_ble_task(),
        mobile_display_task(),
    )


# =============================================================================
# === MAIN LOOP ===============================================================
# =============================================================================

while True:
    current_rssi = {}
    estimated_pos = None
    filtered_pos = None
    stop_flag = False
    rssi_history = {name: [] for name in BEACON_NAMES}

    mode_idx = menu_select("SELECT MODE", ["MOBILE", "BEACON"])

    if mode_idx == 1:
        beacon_idx = menu_select("PICK BEACON", BEACON_NAMES)
        beacon_name = BEACON_NAMES[beacon_idx]

        screen.clear()
        screen.title("BEACON")
        screen.subtitle(beacon_name, "Starting...")
        screen.show()
        sleep_ms(500)

        asyncio.run(run_beacon(beacon_name))

        screen.clear()
        screen.title("STOPPED")
        screen.subtitle("Back to menu")
        screen.show()
        sleep_ms(1000)

    else:
        screen.clear()
        screen.title("TRILATERATION")
        screen.subtitle("Scanning...", "LEFT: menu")
        screen.show()
        sleep_ms(500)

        asyncio.run(run_mobile())

        screen.clear()
        screen.title("STOPPED")
        screen.subtitle("Back to menu")
        screen.show()
        sleep_ms(1000)
