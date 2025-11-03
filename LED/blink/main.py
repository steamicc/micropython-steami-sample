import pyb 
from time import sleep 
import ssd1327
from machine import SPI, Pin

# Initialisation de l'affichage
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")

display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

# Initialisation des LEDs
led_red = pyb.LED(1)
led_green = pyb.LED(2)
led_blue = pyb.LED(3)
delay = 0.5 

# Fonctions pour faire clignoter une LED
def blink_led(led, couleur):
    display.fill(0)
    draw_text(display, "LED Allumée(s) :", 50)
    draw_text(display, f"- LED {couleur}", 70)
    display.show()

    led.on()
    sleep(delay)
    led.off()
    sleep(delay)

# Fonction pour faire clignoter deux LEDs
def blink_two_leds(led1, led2, couleur1, couleur2):
    display.fill(0)
    draw_text(display, "LED Allumée(s) :", 50)
    draw_text(display, f"- LED {couleur1}", 70)
    draw_text(display, f"- LED{couleur2}", 80)
    display.show()

    led1.on()
    led2.on()
    sleep(delay)
    led1.off()
    led2.off()
    sleep(delay)

# Fonction pour faire clignoter toutes les LEDs
def blink_all_leds():
        
    display.fill(0)
    draw_text(display, "LED Allumée(s) :", 50)
    draw_text(display, "Toutes les LEDs", 70)
    display.show()

    led_red.on()
    led_green.on()
    led_blue.on()
    sleep(delay)
    led_red.off()
    led_green.off()
    led_blue.off()
    sleep(delay)

# --- Fonction pour remplacer les accents par ASCII simples ---
def normalize_text(text):
    replacements = {
        'é':'e', 'è':'e', 'ê':'e', 'à':'a', 'ù':'u',
        'ô':'o', 'î':'i', 'ç':'c', 'É':'E', 'À':'A',
        'Ç':'C', 'Ô':'O'
    }
    for accented, simple in replacements.items():
        text = text.replace(accented, simple)
    return text

# Fonction pour afficher le texte avec retour à la ligne et centrage automatique
def draw_text(display, text, y_start, screen_width=128, char_width=8, line_height=8):
    text = normalize_text(text)
    words = text.split(" ")
    line = ""
    y = y_start
    for word in words:
        if len(line + word) * char_width > screen_width:
            x = (screen_width - len(line.rstrip())*char_width) // 2
            display.text(line.rstrip(), x, y)
            y += line_height
            line = word + " "
        else:
            line += word + " "
    # Affiche la dernière ligne
    x = (screen_width - len(line.rstrip())*char_width) // 2
    display.text(line.rstrip(), x, y)

while True:
    blink_led(led_red, "Rouge")
    blink_led(led_green, "Vert")
    blink_led(led_blue, "Bleu")

    blink_two_leds(led_red, led_green, "Rouge", "Vert")
    blink_two_leds(led_red, led_blue, "Rouge", "Bleu")
    blink_two_leds(led_green, led_blue, "Vert", "Bleu")

    blink_all_leds()

