from pins import *
import math
from time import sleep

screens = ["TEXT", "GRAY", "ANIM", "STEAMI", "EXIT"]

def exit_display():
    while True:
        if MENU_BUTTON.value() == 0:
            break

def display_Text():
    display.fill(0)
    for i in range(32, 128):
        j = i - 32
        x = (j % 16) << 3
        y = (j // 16) << 3
        display.text(chr(i), x, y + 40, 1 + (i % 15))
    display.show()
    exit_display()

def display_gray():
    display.fill(0)
    for r in range(16):
        display.framebuf.fill_rect(0, r * 8, 128, 8, r)
    display.show()
    exit_display()

def display_anim():
    display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

    pi = math.pi

    size = 700
    width = display.width
    height = display.height

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

        display.fill(0)

        for i in range(3):
            display.framebuf.line(int(p2x[i]), int(p2y[i]), int(p2x[i + 1]), int(p2y[i + 1]), 1)
            display.framebuf.line(
                int(p2x[i + 4]), int(p2y[i + 4]), int(p2x[i + 5]), int(p2y[i + 5]), 1
            )
            display.framebuf.line(int(p2x[i]), int(p2y[i]), int(p2x[i + 4]), int(p2y[i + 4]), 1)

        display.framebuf.line(int(p2x[3]), int(p2y[3]), int(p2x[0]), int(p2y[0]), 1)
        display.framebuf.line(int(p2x[7]), int(p2y[7]), int(p2x[4]), int(p2y[4]), 1)
        display.framebuf.line(int(p2x[3]), int(p2y[3]), int(p2x[7]), int(p2y[7]), 1)
        display.show()
            
def display_steami():
    display.fill(0)

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
    s = 0
    while True:
        if MENU_BUTTON.value() == 0:
            break
        s = (s + 1) % 2
        for y in range(12):
            for x in range(12):
                display.framebuf.fill_rect((x * 9)+10, (y * 9)+10, 9, 9, smile[s][y][x]*255)
        display.show()
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
            
        if screen_index >= len(screens) : screen_index = 0
        elif screen_index < 0 : screen_index = len(screens) - 1