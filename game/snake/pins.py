import asyncio
from time import sleep
from pyb import Pin

from steami import Screen

# Écran : SSD1327 sur V1a/V1b, GC9A01 sur V1c. begin() le plus tôt possible :
# la mémoire de l'image est réservée à ce moment.
SCREEN = Screen()
SCREEN.begin()

A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)
