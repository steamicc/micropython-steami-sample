from pins import *


def display_pressed(button):
    SCREEN.clear()
    SCREEN.title("BUTTON", WHITE)
    SCREEN.text(button, "CENTER", WHITE)
    SCREEN.show()

async def button_menu():
    SCREEN.clear()
    SCREEN.title("BUTTON", WHITE)
    SCREEN.show()

    print("--- BUTTON ---")

    while True:
        joystick_move = await wait_for_button()
        if joystick_move == "A":
            print("A button pressed")
            display_pressed("A")
        elif joystick_move == "B":
            print("B button pressed")
            display_pressed("B")
        elif joystick_move == "MENU":
            print("Menu button pressed")
            display_pressed("MENU")
            break
