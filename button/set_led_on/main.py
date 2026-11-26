from time import sleep
from pyb import Pin

LED_RED = Pin("LED_RED", Pin.OUT_PP)
LED_GREEN = Pin("LED_GREEN", Pin.OUT_PP)
LED_BLUE = Pin("LED_BLUE", Pin.OUT_PP)

A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

def toggle(pin):
    pin.value(not pin.value())

while True:
    if A_BUTTON.value() == 0:
        print("A_BUTTON pressed")
        toggle(LED_RED)
        sleep(0.2)  # Debounce delay
    elif B_BUTTON.value() == 0:
        print("B_BUTTON pressed")
        toggle(LED_GREEN)
        sleep(0.2)
    elif MENU_BUTTON.value() == 0:
        print("MENU_BUTTON pressed")
        toggle(LED_BLUE)
        sleep(0.2)