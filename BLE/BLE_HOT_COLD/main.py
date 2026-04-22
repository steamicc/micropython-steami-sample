"""BLE Hot/Cold treasure hunt game using aioble and SSD1327 OLED.

Two STeaMi boards run this same file:
    - UP/DOWN to pick TREASURE or SEEKER, RIGHT to confirm
    - LEFT at any time to return to mode selection

The seeker scans for the treasure beacon, maps RSSI to proximity zones,
displays feedback on the OLED and plays buzzer beeps that accelerate
as the player gets closer.

Proximity zones (0-100%):
    COLD    (  0 to 25 ) -> sad face      + 1 slow beep every 3s   (440 Hz)
    WARM    ( 25 to 50 ) -> sleeping face + 1 beep every 1.2s      (660 Hz)
    HOT     ( 50 to 75 ) -> happy face    + 2 fast beeps every 500ms (880 Hz)
    BURNING ( 75 to 100] -> love face     + 3 rapid beeps every 150ms (1200 Hz)

RSSI smoothing uses an Exponential Moving Average (EMA) so the display
reacts immediately to large jumps while staying stable during small
fluctuations. Zone transitions are protected by a hysteresis band to
avoid flickering at zone boundaries.

Hardware:
    - 2 x STM32WB55 BLE radio
    - SSD1327 128x128 OLED display (round)
    - MCP23009E D-PAD (UP/DOWN/LEFT/RIGHT)
    - SPEAKER pin (buzzer)

Learning goals:
    - Practical application of RSSI to distance
    - EMA signal smoothing: reactive yet stable
    - Hysteresis to avoid zone flickering
    - Multi-sensory feedback (screen + sound)
    - Asyncio task coordination
"""

import bluetooth
import uasyncio as asyncio
from time import sleep_us, ticks_ms, ticks_diff

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
from steami_screen import BLUE, RED, Screen, SSD1327Display, YELLOW

# === BLE setup ===
ble = bluetooth.BLE()
ble.active(True)
mac_bytes = ble.config("mac")[1]
mac_suffix = "".join(f"{b:02X}" for b in mac_bytes[-2:])
DEVICE_NAME = f"STeaMi-{mac_suffix}"
BEACON_NAME = "Beacon_M1"

# === Display ===
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = SSD1327Display(ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs))
screen = Screen(display)

# === Buzzer ===
speaker = Pin("SPEAKER", Pin.OUT)

# === Buttons ===
i2c = I2C(1)
reset_expander = Pin("RST_EXPANDER", Pin.OUT)
mcp = MCP23009E(i2c, address=MCP23009_I2C_ADDR, reset_pin=reset_expander)

_DPAD = {
    MCP23009_BTN_UP: "UP",
    MCP23009_BTN_DOWN: "DOWN",
    MCP23009_BTN_LEFT: "LEFT",
    MCP23009_BTN_RIGHT: "RIGHT",
}


def setup_buttons():
    for pin in _DPAD:
        mcp.setup(pin, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)


def _read_button():
    """Return the name of the currently pressed button, or None."""
    for pin, name in _DPAD.items():
        if mcp.get_level(pin) == MCP23009_LOGIC_LOW:
            return name
    return None


# =============================================================================
# === CALIBRATION =============================================================
# =============================================================================
# Adjust these two values to match your environment:
#   - Hold boards 1-2 cm apart, note the RSSI -> set RSSI_MAX
#   - Hold boards ~5 m apart,   note the RSSI -> set RSSI_MIN
RSSI_MIN = -80  # dBm -- considered far (cold)
RSSI_MAX = -30  # dBm -- considered very close (burning)

# EMA weight: 0.0 = frozen, 1.0 = no smoothing.
# 0.4 reacts quickly to large jumps while dampening noise.
EMA_ALPHA = 0.4

# =============================================================================
# === BLE / TIMING PARAMETERS =================================================
# =============================================================================
ADV_INTERVAL_US = 50_000   # beacon advertising interval (50 ms)
ADV_TIMEOUT_MS = 100       # short window per advertise() call
SCAN_DURATION_MS = 200     # scan burst -- shorter = more reactive
SIGNAL_TIMEOUT_MS = 3000   # declare signal lost after this many ms with no packet
DISPLAY_INTERVAL_MS = 150  # OLED refresh rate (decoupled from BLE scan)

MODE_SELECTION_S = 10  # auto-confirm countdown

# =============================================================================
# === PROXIMITY ZONES =========================================================
# =============================================================================
ZONE_COLD = 25
ZONE_WARM = 50
ZONE_HOT = 75

# Dead-band around each threshold: must cross by this % to change zone.
# 8% absorbs typical BLE RSSI noise (~5 dBm on a 50 dBm scale = 10%).
ZONE_HYSTERESIS = 8

_ZONE_DATA = [
    ("COLD",     BLUE,   "sad"),
    ("WARM",     YELLOW, "sleeping"),
    ("HOT",      RED,    "happy"),
    ("BURNING!", RED,    "love"),
]

# Beep patterns per zone: (frequency Hz, single-beep duration ms, beep count, gap between beeps ms)
# Rhythm changes make zones unmistakable even with eyes closed.
_ZONE_BEEP = [
    (440,  80, 1,  0),   # COLD    -- one low slow beep
    (660, 100, 1,  0),   # WARM    -- one medium beep
    (880,  70, 2, 80),   # HOT     -- da-dum  da-dum
    (1200, 55, 3, 50),   # BURNING -- rapid triple burst
]

# Time to wait AFTER each beep group before the next one (ms).
_ZONE_INTERVAL = (3000, 1200, 500, 150)

# =============================================================================
# === SHARED STATE ============================================================
# =============================================================================
current_rssi = float(RSSI_MIN)  # EMA-smoothed RSSI
last_beacon_ticks = 0
beacon_seen = False
current_zone_idx = 0  # 0=COLD, 1=WARM, 2=HOT, 3=BURNING
_exit_requested = False


# =============================================================================
# === BUZZER ==================================================================
# =============================================================================


async def tone_async(freq, duration_ms):
    """Play a short blocking tone, then yield to the event loop."""
    if freq == 0:
        await asyncio.sleep_ms(duration_ms)
        return
    period_us = int(1_000_000 / freq)
    half = period_us // 2
    cycles = (duration_ms * 1000) // period_us
    for _ in range(cycles):
        speaker.on()
        sleep_us(half)
        speaker.off()
        sleep_us(half)
    await asyncio.sleep_ms(0)


async def beep_pattern(zone_idx):
    """Play the beep pattern for the given zone."""
    freq, dur, count, gap = _ZONE_BEEP[zone_idx]
    for i in range(count):
        await tone_async(freq, dur)
        if gap and i < count - 1:
            await asyncio.sleep_ms(gap)


async def _wait_ms(ms):
    """Wait for up to ms, waking early on exit, signal loss, or zone change."""
    zone = current_zone_idx
    elapsed = 0
    while elapsed < ms:
        if _exit_requested or not beacon_seen or current_zone_idx != zone:
            return
        await asyncio.sleep_ms(50)
        elapsed += 50


async def buzzer_task():
    """Play beep patterns that reflect the current proximity zone."""
    while not _exit_requested:
        if not beacon_seen:
            # Slow searching pulse; wake immediately when beacon appears.
            await tone_async(350, 50)
            await _wait_ms(1000)
            continue

        zone = current_zone_idx
        await beep_pattern(zone)
        await _wait_ms(_ZONE_INTERVAL[zone])


# =============================================================================
# === HELPERS =================================================================
# =============================================================================


def build_adv_payload(name):
    """Minimal BLE advertising payload carrying the device name."""
    name_bytes = name.encode()
    return bytes((len(name_bytes) + 1, 0x09)) + name_bytes


def rssi_to_proximity(rssi):
    """Map smoothed RSSI to a 0-100 proximity percentage."""
    clamped = max(RSSI_MIN, min(RSSI_MAX, rssi))
    return int((clamped - RSSI_MIN) / (RSSI_MAX - RSSI_MIN) * 100)


def update_zone(proximity):
    """Advance or retreat one zone at a time using hysteresis."""
    global current_zone_idx
    z = current_zone_idx
    thresholds = (ZONE_COLD, ZONE_WARM, ZONE_HOT)
    if z < 3 and proximity >= thresholds[z] + ZONE_HYSTERESIS:
        z += 1
    elif z > 0 and proximity < thresholds[z - 1] - ZONE_HYSTERESIS:
        z -= 1
    current_zone_idx = z


async def _sleep_interruptible(ms):
    """Sleep for ms, waking up early if _exit_requested is set."""
    while ms > 0 and not _exit_requested:
        await asyncio.sleep_ms(min(100, ms))
        ms -= 100


# =============================================================================
# === MODE SELECTION ==========================================================
# =============================================================================

_MODES = ["TREASURE", "SEEKER"]


def _draw_mode_select(selected, remaining):
    screen.clear()
    screen.title("SELECT MODE")
    screen.menu(_MODES, selected=selected)
    screen.subtitle("U/D:select", "RIGHT:OK", f"{remaining}s")
    screen.show()


async def select_mode_async():
    """Menu-driven mode selection with D-PAD and auto-confirm countdown."""
    global _exit_requested
    _exit_requested = False

    selected = 1  # Default: SEEKER
    last_btn = None
    remaining = MODE_SELECTION_S

    # Wait for any held button from the previous mode to release
    while _read_button() is not None:
        await asyncio.sleep_ms(20)

    while remaining > 0:
        _draw_mode_select(selected, remaining)
        for _ in range(20):  # 20 * 50 ms = 1 s per countdown tick
            btn = _read_button()
            if btn != last_btn:
                if btn == "UP":
                    selected = 0
                    _draw_mode_select(selected, remaining)
                elif btn == "DOWN":
                    selected = 1
                    _draw_mode_select(selected, remaining)
                elif btn == "RIGHT":
                    _draw_mode_select(selected, 0)
                    await asyncio.sleep_ms(300)
                    return selected == 0
            last_btn = btn
            await asyncio.sleep_ms(50)
        remaining -= 1

    return selected == 0  # True = TREASURE


# =============================================================================
# === EXIT WATCHER ============================================================
# =============================================================================


async def exit_watcher_task():
    """Set _exit_requested when LEFT is pressed, then return."""
    global _exit_requested
    while _read_button() is not None:
        await asyncio.sleep_ms(20)
    while True:
        if _read_button() == "LEFT":
            while _read_button() is not None:
                await asyncio.sleep_ms(20)
            _exit_requested = True
            return
        await asyncio.sleep_ms(50)


# =============================================================================
# === TREASURE MODE (BEACON) ==================================================
# =============================================================================


async def treasure_ble_task():
    """Advertise as the treasure beacon until exit is requested."""
    adv_payload = build_adv_payload(BEACON_NAME)
    print(f"Treasure mode: advertising as {BEACON_NAME}")
    while not _exit_requested:
        try:
            await aioble.advertise(
                interval_us=ADV_INTERVAL_US,
                adv_data=adv_payload,
                connectable=False,
                timeout_ms=ADV_TIMEOUT_MS,
            )
        except asyncio.TimeoutError:
            pass


async def treasure_display_task():
    """Show treasure mode on OLED until exit is requested."""
    while not _exit_requested:
        screen.clear()
        screen.title("TREASURE")
        screen.face("love")
        screen.subtitle("Find me!", BEACON_NAME, "LEFT: menu")
        screen.show()
        await _sleep_interruptible(2000)


async def run_treasure():
    screen.clear()
    screen.title("TREASURE")
    screen.face("love")
    screen.subtitle("Starting...")
    screen.show()
    await asyncio.sleep_ms(800)
    await asyncio.gather(
        treasure_ble_task(),
        treasure_display_task(),
        exit_watcher_task(),
    )


# =============================================================================
# === SEEKER MODE (SCANNER) ===================================================
# =============================================================================


async def seeker_ble_task():
    """Scan for the treasure beacon and update shared state with EMA smoothing."""
    global current_rssi, last_beacon_ticks, beacon_seen, current_zone_idx
    first_sample = True
    while not _exit_requested:
        async with aioble.scan(
            SCAN_DURATION_MS,
            interval_us=10000,
            window_us=10000,
            active=True,
        ) as scanner:
            async for result in scanner:
                if _exit_requested:
                    break
                if result.name() != BEACON_NAME:
                    continue
                raw = result.rssi
                if first_sample:
                    current_rssi = float(raw)
                    first_sample = False
                else:
                    current_rssi = EMA_ALPHA * raw + (1 - EMA_ALPHA) * current_rssi
                proximity = rssi_to_proximity(current_rssi)
                prev_zone = current_zone_idx
                update_zone(proximity)
                last_beacon_ticks = ticks_ms()
                beacon_seen = True
                if current_zone_idx != prev_zone:
                    print(
                        f"ema={current_rssi:.1f} dBm  prox={proximity}%"
                        f"  -> {_ZONE_DATA[current_zone_idx][0]}"
                    )

        if _exit_requested:
            break

        if beacon_seen and ticks_diff(ticks_ms(), last_beacon_ticks) > SIGNAL_TIMEOUT_MS:
            beacon_seen = False
            first_sample = True
            current_rssi = float(RSSI_MIN)
            current_zone_idx = 0
            print("Signal lost")


async def seeker_display_task():
    """Refresh OLED at a fixed rate from shared state."""
    while not _exit_requested:
        screen.clear()
        if beacon_seen:
            proximity = rssi_to_proximity(current_rssi)
            label, color, face = _ZONE_DATA[current_zone_idx]
            screen.gauge(proximity, min_val=0, max_val=100, color=color)
            screen.title(label)
            screen.face(face, compact=True)
            screen.subtitle(f"{int(current_rssi)} dBm", f"{proximity}%")
        else:
            screen.title("SEARCHING...")
            screen.face("surprised")
            screen.subtitle("Looking for", BEACON_NAME)
        screen.show()
        await asyncio.sleep_ms(DISPLAY_INTERVAL_MS)


async def run_seeker():
    global beacon_seen, current_rssi, current_zone_idx
    beacon_seen = False
    current_rssi = float(RSSI_MIN)
    current_zone_idx = 0

    screen.clear()
    screen.title("SEEKER")
    screen.face("surprised")
    screen.subtitle("Starting...", "LEFT: menu")
    screen.show()
    await asyncio.sleep_ms(800)
    await asyncio.gather(
        seeker_ble_task(),
        seeker_display_task(),
        buzzer_task(),
        exit_watcher_task(),
    )


# =============================================================================
# === MAIN LOOP ===============================================================
# =============================================================================


async def main():
    setup_buttons()
    while True:
        is_treasure = await select_mode_async()
        if is_treasure:
            await run_treasure()
        else:
            await run_seeker()


asyncio.run(main())
