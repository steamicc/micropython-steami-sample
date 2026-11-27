from pins import *
import math
from time import sleep

from steami_screen import BLACK, BLUE, DARK, GRAY, GREEN, LIGHT, RED, WHITE, YELLOW

screens = ["TEXT", "GRAY", "ANIM", "STEAMI", "EXIT"]

def exit_display():
    while True:
        if MENU_BUTTON.value() == 0:
            break

def display_Text():
    # 16 columns on the 128 px screen; 12 on the round 240 px screen of the
    # V1c (glyphs twice as big), so that the block stays inside the circle.
    k = SCREEN.k
    cell = 8 * k
    cols = 16 if k == 1 else 12
    rows = (96 + cols - 1) // cols
    x0 = (SCREEN.width - cols * cell) // 2
    y0 = (SCREEN.height - rows * cell) // 2
    colors = (WHITE, LIGHT, GRAY, DARK, GREEN, RED, BLUE, YELLOW)
    SCREEN.clear()
    for i in range(32, 128):
        j = i - 32
        x = x0 + (j % cols) * cell
        y = y0 + (j // cols) * cell
        SCREEN.text(chr(i), (x, y), colors[i % len(colors)], k)
    SCREEN.show()
    exit_display()

def display_gray():
    grays = (BLACK, DARK, GRAY, LIGHT, WHITE)
    SCREEN.clear()
    for r, color in enumerate(grays):
        y = r * SCREEN.height // len(grays)
        h = (r + 1) * SCREEN.height // len(grays) - y
        SCREEN.rect(0, y, SCREEN.width, h, color, fill=True)
    SCREEN.show()
    exit_display()

def display_anim():
    pi = math.pi

    size = SCREEN.u(700)
    width = SCREEN.width
    height = SCREEN.height

    d = 3
    px = [-d, d, d, -d, -d, d, d, -d]
    py = [-d, -d, d, d, -d, -d, d, d]
    pz = [-d, -d, -d, -d, d, d, d, d]

    p2x = [0, 0, 0, 0, 0, 0, 0, 0]
    p2y = [0, 0, 0, 0, 0, 0, 0, 0]
    r = [0, 0, 0]

    while True:
        if MENU_BUTTON.value() == 0:
            break
        r[0] = r[0] + pi / 180.0
        r[1] = r[1] + pi / 180.0
        r[2] = r[2] + pi / 180.0
        if r[0] >= 360.0 * pi / 180.0:
            r[0] = 0
        if r[1] >= 360.0 * pi / 180.0:
            r[1] = 0
        if r[2] >= 360.0 * pi / 180.0:
            r[2] = 0

        for i in range(8):
            px2 = px[i]
            py2 = math.cos(r[0]) * py[i] - math.sin(r[0]) * pz[i]
            pz2 = math.sin(r[0]) * py[i] + math.cos(r[0]) * pz[i]

            px3 = math.cos(r[1]) * px2 + math.sin(r[1]) * pz2
            py3 = py2
            pz3 = -math.sin(r[1]) * px2 + math.cos(r[1]) * pz2

            ax = math.cos(r[2]) * px3 - math.sin(r[2]) * py3
            ay = math.sin(r[2]) * px3 + math.cos(r[2]) * py3
            az = pz3 - 150

            p2x[i] = width / 2 + ax * size / az
            p2y[i] = height / 2 + ay * size / az

        SCREEN.clear()

        for i in range(3):
            SCREEN.line(int(p2x[i]), int(p2y[i]), int(p2x[i + 1]), int(p2y[i + 1]), WHITE)
            SCREEN.line(
                int(p2x[i + 4]), int(p2y[i + 4]), int(p2x[i + 5]), int(p2y[i + 5]), WHITE
            )
            SCREEN.line(int(p2x[i]), int(p2y[i]), int(p2x[i + 4]), int(p2y[i + 4]), WHITE)

        SCREEN.line(int(p2x[3]), int(p2y[3]), int(p2x[0]), int(p2y[0]), WHITE)
        SCREEN.line(int(p2x[7]), int(p2y[7]), int(p2x[4]), int(p2y[4]), WHITE)
        SCREEN.line(int(p2x[3]), int(p2y[3]), int(p2x[7]), int(p2y[7]), WHITE)
        SCREEN.show()

def display_steami():
    SCREEN.clear()

    smile =[
            [[0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,0,0,0,0,1,1,1,0],
            [1,1,1,1,1,0,0,1,1,1,1,1],
            [1,1,0,1,1,0,0,1,1,0,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],]
            ,
            [[0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,0,0,0,0,1,1,1,0],
            [1,1,1,1,1,0,0,1,1,1,1,1],
            [1,1,1,0,1,0,0,1,1,1,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],]
            ,
            ]
    # 9 px cells on the 128 px screen, the grid centred on the screen.
    cell = SCREEN.u(9)
    offset = (SCREEN.width - 12 * cell) // 2
    s = 0
    while True:
        if MENU_BUTTON.value() == 0:
            break
        s = (s + 1) % 2
        for y in range(12):
            for x in range(12):
                color = WHITE if smile[s][y][x] else BLACK
                SCREEN.rect((x * cell) + offset, (y * cell) + offset, cell, cell, color, fill=True)
        SCREEN.show()
        sleep(1)

def show_screens(index):
    if index == 0:
        display_Text()
    elif index == 1:
        display_gray()
    elif index == 2:
        display_anim()
    elif index == 3:
        display_steami()


async def screen_menu():
    print("--- SCREEN ---")
    screen_index = 0
    while True:
        display_menu("SCREEN", screens, screen_index)
        btn = await wait_for_button()
        if btn == "A":
            print("A")
            screen_index -= 1
        elif btn == "B":
            print("B")
            screen_index += 1
        elif btn == "MENU":
            if screens[screen_index] == "EXIT":
                break
            show_screens(screen_index)
            sleep(0.3)

        if screen_index >= len(screens) :
            screen_index = 0
        elif screen_index < 0 :
            screen_index = len(screens) - 1
