"""BLE trilateration indoor positioning example using aioble and SSD1327 OLED.

3 fixed beacon boards broadcast their identity. A mobile board scans all 3,
converts RSSI to distance using the log-distance path loss model, then
trilaterates a 2D position displayed as a dot on a live map.

Roles (single file):
    - Navigate menu with UP/DOWN, confirm with RIGHT
    - BEACON mode: select beacon ID (M1/M2/M3) and advertise continuously
    - MOBILE mode: scan all beacons, trilaterate and display live position

Path loss model (per beacon):
    d = 10 ^ ((RSSI_ref - RSSI) / (10 * n))
    RSSI_ref: measured at 1m with nRF Connect (iPhone 17 Pro Max)
    n: computed from 1m and 2m measurements per beacon

Calibration data:
    Beacon   RSSI@1m   RSSI@2m   n
    M1       -75       -87       3.99
    M2       -75       -88       4.32
    M3       -80       -88       2.66

Beacon coordinates (cm, measured on site):
    M1 = (  0,   0)
    M2 = (420,   0)
    M3 = (330, 278)

Hardware:
    - 4 STeaMi boards (3 beacons + 1 mobile)
    - SSD1327 128x128 OLED on mobile board
    - D-PAD for menu navigation
"""

import bluetooth
import math
import uasyncio as asyncio
from time import sleep_ms

import aioble
import ssd1327
from machine import I2C, SPI, Pin
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
from steami_screen import DARK, GRAY, LIGHT, Screen, SSD1327Display, WHITE

# === BLE setup ===
ble = bluetooth.BLE()
ble.active(True)

mac_bytes = ble.config("mac")[1]
mac_suffix = "".join(f"{b:02X}" for b in mac_bytes[-2:])
DEVICE_NAME = f"STeaMi-{mac_suffix}"

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
    (0 + 420 + 330) // 3,
    (0 + 0 + 278) // 3,
)

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

# === Display ===
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = SSD1327Display(ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs))
screen = Screen(display)

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
MAP_X = 28
MAP_Y = 14
MAP_W = 72
MAP_H = 72

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


def menu_select(title, items):
    """Generic D-PAD menu. Returns selected index."""
    selected = 0
    while True:
        screen.clear()
        screen.title(title)
        screen.menu(items, selected=selected)
        screen.subtitle("UP/DOWN: nav", "RIGHT: confirm")
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
    """Apply exponential smoothing with minimum movement threshold."""
    global filtered_pos

    if filtered_pos is None:
        filtered_pos = new_pos
        return filtered_pos

    fx = ALPHA * new_pos[0] + (1 - ALPHA) * filtered_pos[0]
    fy = ALPHA * new_pos[1] + (1 - ALPHA) * filtered_pos[1]

    dx = fx - filtered_pos[0]
    dy = fy - filtered_pos[1]
    if math.sqrt(dx * dx + dy * dy) < MIN_MOVE_CM:
        return filtered_pos

    filtered_pos = (fx, fy)
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
        screen.subtitle(beacon_name, "Broadcasting...", "LEFT: menu")
        screen.show()
        await asyncio.sleep_ms(1000)


async def beacon_button_task():
    """Watch for LEFT button to exit beacon mode."""
    global stop_flag
    while not stop_flag:
        if is_pressed(MCP23009_BTN_LEFT):
            wait_released(MCP23009_BTN_LEFT)
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
                    current_rssi[name] = smooth_rssi(name, result.rssi)


async def mobile_display_task():
    """Compute trilateration, filter position and display live map."""
    global estimated_pos, stop_flag

    d = screen._d

    while not stop_flag:
        if is_pressed(MCP23009_BTN_LEFT):
            wait_released(MCP23009_BTN_LEFT)
            stop_flag = True
            break

        # Compute distances from smoothed RSSI
        distances = {
            name: rssi_to_distance(current_rssi[name], name)
            for name in BEACON_NAMES
            if name in current_rssi
        }

        # Trilaterate and filter
        if len(distances) == 3:
            raw_pos = trilaterate(distances)
            if raw_pos:
                estimated_pos = apply_filter(raw_pos)

        # Draw map
        screen.clear()
        screen._rect(MAP_X, MAP_Y, MAP_W, MAP_H, DARK)

        # Draw beacon markers with labels
        for name, (cx, cy) in BEACON_POS.items():
            px, py = world_to_screen(cx, cy)
            screen._fill_rect(px - 3, py - 3, 6, 6, LIGHT)
            short = name[-2:]
            lx = px - 8
            ly = py - 14 if py > MAP_Y + 20 else py + 8
            d.text(short, lx, ly, GRAY)

        # Draw filtered position
        if estimated_pos:
            ex = max(0, min(SPACE_W, estimated_pos[0]))
            ey = max(0, min(SPACE_H, estimated_pos[1]))
            px, py = world_to_screen(ex, ey)
            screen._fill_circle(px, py, 3, WHITE)

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
        beacon_idx = menu_select("SELECT BEACON", BEACON_NAMES)
        beacon_name = BEACON_NAMES[beacon_idx]

        screen.clear()
        screen.title("BEACON")
        screen.subtitle(beacon_name, "Starting...")
        screen.show()
        sleep_ms(500)

        asyncio.run(run_beacon(beacon_name))

        screen.clear()
        screen.title("BEACON STOPPED")
        screen.subtitle("Returning to menu...")
        screen.show()
        sleep_ms(1000)

    else:
        screen.clear()
        screen.title("TRILATERATION")
        screen.subtitle("Scanning beacons...", "LEFT: menu")
        screen.show()
        sleep_ms(500)

        asyncio.run(run_mobile())

        screen.clear()
        screen.title("STOPPED")
        screen.subtitle("Returning to menu...")
        screen.show()
        sleep_ms(1000)
