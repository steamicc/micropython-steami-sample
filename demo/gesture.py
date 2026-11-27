from pins import *
from time import sleep

from steami import Gesture

gesture = Gesture()


def display_gesture(text):
    SCREEN.clear()
    SCREEN.title("GESTURE", WHITE)
    display_line(text, 50)
    display_line("MENU: back", 90)
    SCREEN.show()


async def gesture_menu():
    print("--- GESTURE ---")

    # The APDS-9960 is on V1a and V1b only: on a V1c, begin() returns False.
    if not gesture.begin():
        print("No gesture sensor:", gesture.error())
        display_gesture("No sensor")
        while MENU_BUTTON.value() != 0:
            sleep(0.1)
        sleep(0.2)
        return

    display_gesture("Move a hand")
    while True:
        if MENU_BUTTON.value() == 0:
            sleep(0.2)
            return
        direction = gesture.read(200)
        if direction != Gesture.NONE:
            name = Gesture.name(direction)
            print("Gesture:", name)
            display_gesture(name)
