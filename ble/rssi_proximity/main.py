"""BLE RSSI proximity detector example using aioble and SSD1327 OLED.

Two STeaMi boards run this same file:
    - Hold button UP during the 10-second startup window → BEACON mode
    - Release button UP → SCANNER mode (default)

The scanner reads the RSSI of the beacon and maps it to a proximity level
displayed as a gauge on the round OLED. RSSI is averaged over N samples
to reduce noise while keeping fast response.

Hardware:
    - 2 x STM32WB55 BLE radio
    - SSD1327 128x128 OLED display (round)
    - MCP23009E D-PAD (button UP used for mode selection)

Learning goals:
    - BLE scanning with aioble
    - RSSI as a proxy for distance
    - Signal averaging to reduce noise
"""

import sys

sys.path.insert(0, "/remote")

import bluetooth
import uasyncio as asyncio
from time import sleep_ms

import aioble
import ssd1327
from machine import I2C, SPI, Pin
from mcp23009e import MCP23009E
from mcp23009e.const import (
    MCP23009_BTN_UP,
    MCP23009_DIR_INPUT,
    MCP23009_I2C_ADDR,
    MCP23009_LOGIC_LOW,
    MCP23009_PULLUP,
)
from steami_screen import GRAY, LIGHT, RED, Screen, SSD1327Display

# === BLE setup ===
ble = bluetooth.BLE()
ble.active(True)

mac_bytes = ble.config("mac")[1]
mac_suffix = "".join(f"{b:02X}" for b in mac_bytes[-2:])
DEVICE_NAME = f"STeaMi-{mac_suffix}"
BEACON_NAME = "STeaMi-BEACON"

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
mcp.setup(MCP23009_BTN_UP, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)

# === BLE parameters ===
ADV_INTERVAL_US = 50_000  # 50ms beacon interval for fast detection
ADV_TIMEOUT_MS = 100  # Short advertising window
SCAN_DURATION_MS = 500  # Very short scan bursts for fast response
RSSI_SAMPLES = 2  # Few samples for fast reaction
RSSI_MIN = -90  # dBm considered far
RSSI_MAX = -30  # dBm considered very close

# === Mode selection window ===
MODE_SELECTION_S = 10

# === Shared state ===
rssi_samples = []
current_rssi = RSSI_MIN


def build_adv_payload(name):
    """Build a minimal BLE advertising payload with device name."""
    payload = bytearray()
    name_bytes = name.encode()
    payload += bytes((len(name_bytes) + 1, 0x09)) + name_bytes
    return payload


def rssi_to_proximity(rssi):
    """Map RSSI value to a 0-100 proximity percentage."""
    clamped = max(RSSI_MIN, min(RSSI_MAX, rssi))
    return int((clamped - RSSI_MIN) / (RSSI_MAX - RSSI_MIN) * 100)


def rssi_to_color(proximity):
    """Return display color based on proximity level."""
    if proximity > 70:
        return RED
    elif proximity > 40:
        return LIGHT
    else:
        return GRAY


def select_mode():
    """Show a 10-second countdown and detect button UP to select mode."""
    print("Hold UP button for BEACON mode, release for SCANNER mode.")
    for remaining in range(MODE_SELECTION_S, 0, -1):
        screen.clear()
        screen.title("SELECT MODE")
        screen.subtitle(
            "Hold UP: BEACON",
            "Release: SCANNER",
            f"Starting in {remaining}s...",
        )
        screen.show()
        sleep_ms(1000)
        if mcp.get_level(MCP23009_BTN_UP) == MCP23009_LOGIC_LOW:
            print("Button UP held -> BEACON mode")
            return True
    print("Button UP released -> SCANNER mode")
    return False


# =============================================================================
# === BEACON MODE =============================================================
# =============================================================================


async def beacon_ble_task():
    """Advertise as STeaMi-BEACON continuously."""
    adv_payload = build_adv_payload(BEACON_NAME)
    print(f"Beacon mode: advertising as {BEACON_NAME}")
    while True:
        try:
            await aioble.advertise(
                interval_us=ADV_INTERVAL_US,
                adv_data=adv_payload,
                connectable=False,
                timeout_ms=ADV_TIMEOUT_MS,
            )
        except asyncio.TimeoutError:
            pass


async def beacon_display_task():
    """Show beacon status on OLED."""
    while True:
        screen.clear()
        screen.title("BEACON")
        screen.subtitle(BEACON_NAME, "Broadcasting...")
        screen.show()
        await asyncio.sleep_ms(1000)


async def run_beacon():
    await asyncio.gather(
        beacon_ble_task(),
        beacon_display_task(),
    )


# =============================================================================
# === SCANNER MODE ============================================================
# =============================================================================


async def scanner_ble_task():
    global current_rssi
    display_counter = 0
    while True:
        async with aioble.scan(
            SCAN_DURATION_MS,
            interval_us=10000,
            window_us=10000,
            active=True,
        ) as scanner:
            async for result in scanner:
                if result.name() == BEACON_NAME:
                    current_rssi = result.rssi  # Valeur brute directe
                    print(f"RSSI: {current_rssi} dBm")
                    display_counter += 1
                    if display_counter >= 3:
                        display_counter = 0
                        proximity = rssi_to_proximity(current_rssi)
                        color = rssi_to_color(proximity)
                        screen.clear()
                        screen.title("PROXIMITY")
                        screen.gauge(proximity, min_val=0, max_val=100, color=color)
                        screen.value(str(current_rssi), unit="dBm")
                        screen.subtitle(f"{proximity}%")
                        screen.show()


async def run_scanner():
    await scanner_ble_task()


# =============================================================================
# === ENTRY POINT =============================================================
# =============================================================================

is_beacon = select_mode()

if is_beacon:
    screen.clear()
    screen.title("BEACON MODE")
    screen.subtitle("Starting...")
    screen.show()
    sleep_ms(1000)
    asyncio.run(run_beacon())
else:
    screen.clear()
    screen.title("SCANNER MODE")
    screen.subtitle("Starting...")
    screen.show()
    sleep_ms(1000)
    asyncio.run(run_scanner())
