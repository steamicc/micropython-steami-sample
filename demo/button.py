from pins import *

button_menu = ["A", "B", "MENU"]

def display_pressed(button):
    display.fill(0)
    display.text("BUTTON", 45, 20, 255)
    display.text(button, 60, 60, 255)
    display.show()

async def button_menu():
    display.fill(0)
    display.text("BUTTON", 45, 20, 255)
    display.show()

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
