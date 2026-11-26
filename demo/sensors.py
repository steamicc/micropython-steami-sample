from pins import *
from time import sleep


def display_sensor():
    display.fill(0)
    display.text("SENSORS", 45, 20)
    display.text(f"Temp: {round(SENSOR.temperature(), 1)} C", 5, 40)
    display.text(f"Humid: {round(SENSOR.humidity(), 1)} %", 5, 50)
    display.text(f"Dist: {DISTANCE.read()}mm", 5, 60)
    display.text(f"Lum: {apds.readAmbientLight()}mm", 5, 70)
    display.show()

async def sensor_menu():
    print("--- SENSORS ---")
    apds.enableLightSensor()

    display_sensor()

    while True:
        if MENU_BUTTON.value() == 0:
            sleep(0.2)
            return
        sleep(0.1)
        display_sensor()