import asyncio
from time import sleep

#other files
from pins import *

from led import *
from button import *
from buzzer import *
from ble import *
from sensors import *
from gesture import *
from screen import *


menu = ["LED", "BUTTON", "BUZZER","SENSORS","SCREEN","BLE"]

async def run_menu(menu_index):
    if menu_index == 0:
        await led_menu()
    elif menu_index == 1:
        await button_menu()
    elif menu_index == 2:
        await buzzer_menu()
    elif menu_index == 3:
        await sensor_menu()
    elif menu_index == 4:
        await screen_menu()
    elif menu_index == 5:
        await ble_menu()

async def main_menu():
    menu_index = 0

    while True:
        display_menu("MENU", menu, menu_index)
        print(f"> {menu[menu_index]}")

        btn = await wait_for_button()

        if btn == "A":
            menu_index -= 1
        elif btn == "B":
            menu_index += 1
        elif btn == "MENU":
            await run_menu(menu_index)
            print("--- MAIN ---")
        
        if menu_index >= len(menu):
            menu_index = 0
        elif menu_index < 0:
            menu_index = len(menu) - 1

asyncio.run(main_menu())