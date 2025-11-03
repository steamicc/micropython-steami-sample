from time import sleep
from machine import SPI, Pin, I2C
import ssd1327
from bq27441 import BQ27441

# --- Configuration de l'écran OLED ---
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")

display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

# --- Configuration I2C pour le BQ27441 ---
bus = I2C(1)
fg = BQ27441(bus)

def centerText(text, y):
    length = len(text)
    position = (128 - (length * 8)) // 2
    display.text(text, position, y)

# --- Fonction pour afficher les infos sur l'écran ---
def update_display():
    display.fill(0)  # Efface l'écran
    centerText("Fuel Gauge", 15)
    centerText("================", 25)
    centerText("SoC: {}%".format(fg.state_of_charge()), 40)
    centerText("Volt: {} mV".format(fg.voltage()), 55)
    centerText("Iavg: {} mA".format(fg.current_average()), 70)
    centerText("Full: {} mAh".format(fg.capacity_full()), 85)
    centerText("Rem: {} mAh".format(fg.capacity_remaining()), 100)
    display.show()  # Met à jour l'affichage

# --- Boucle principale ---
while True:
    update_display()
    sleep(2)  # Met à jour toutes les 2 secondes
