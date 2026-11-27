from pins import *
from time import sleep


def display_sensor():
    lines = [
        f"Temp: {round(TEMPERATURE.read(), 1)} C",
        f"Humid: {round(HUMIDITY.read(), 1)} %",
        f"Dist: {DISTANCE.read()}mm",
        f"Lum: {LIGHT.read()}",
    ]
    # One block, left-aligned and centred on the widest line and on the
    # screen centre, so that it stays inside the round screen of the V1c.
    # Cells of 8 px wide, SCREEN.text_height() px high (8 on 128 px, 16 on
    # 240 px); a line every cell height + 2k px (10 on 128 px, 20 on 240 px).
    h = SCREEN.text_height()
    step = h + 2 * SCREEN.k
    x = (SCREEN.width - max(len(line) for line in lines) * 8) // 2
    y = SCREEN.center[1] - (3 * step + h) // 2
    SCREEN.clear()
    SCREEN.title("SENSORS", WHITE)
    for i, line in enumerate(lines):
        SCREEN.text(line, (x, y + i * step), WHITE)
    SCREEN.show()

async def sensor_menu():
    print("--- SENSORS ---")

    display_sensor()

    while True:
        if MENU_BUTTON.value() == 0:
            sleep(0.2)
            return
        sleep(0.1)
        display_sensor()
