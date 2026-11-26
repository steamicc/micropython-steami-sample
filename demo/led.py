from pins import *

import asyncio
from time import sleep

leds = ["RED", "BLUE", "GREEN", "EXIT"]

def run_led(led_index):
    if led_index == 0:
        toggle(LED_RED)
    elif led_index == 1:
        toggle(LED_BLUE)
    elif led_index == 2:    
        toggle(LED_GREEN)
    elif led_index == 3:
        return 

def toggle(pin):
    pin.value(not pin.value())

async def led_menu():
    print("--- LED ---")

    led_index = 0

    while True:
        display_menu("LED", leds, led_index)
        print(f"> {leds[led_index]}")

        joystick_move = await wait_for_button()
        if joystick_move == "A":
            led_index -= 1
        elif joystick_move == "B":
            led_index += 1
        elif joystick_move == "MENU":
            if leds[led_index] == "EXIT":
                break
            run_led(led_index)
            
        if led_index >= len(leds) : led_index = 0
        elif led_index < 0 : led_index = len(leds) - 1