import pyb
from time import sleep
from steami import Screen

# Initialisation de l'affichage (au plus tôt : la mémoire de l'image est allouée ici)
SCREEN = Screen()
SCREEN.begin()

# Initialisation des LEDs
led_red = pyb.LED(1)
led_green = pyb.LED(2)
led_blue = pyb.LED(3)
delay = 0.5

# Fonctions pour faire clignoter une LED
def blink_led(led, couleur):
    SCREEN.clear()
    draw_text("LED Allumée(s) :", SCREEN.u(50))
    draw_text(f"- LED {couleur}", SCREEN.u(70))
    SCREEN.show()

    led.on()
    sleep(delay)
    led.off()
    sleep(delay)

# Fonction pour faire clignoter deux LEDs
def blink_two_leds(led1, led2, couleur1, couleur2):
    SCREEN.clear()
    draw_text("LED Allumée(s) :", SCREEN.u(50))
    draw_text(f"- LED {couleur1}", SCREEN.u(70))
    draw_text(f"- LED{couleur2}", SCREEN.u(80))
    SCREEN.show()

    led1.on()
    led2.on()
    sleep(delay)
    led1.off()
    led2.off()
    sleep(delay)

# Fonction pour faire clignoter toutes les LEDs
def blink_all_leds():

    SCREEN.clear()
    draw_text("LED Allumée(s) :", SCREEN.u(50))
    draw_text("Toutes les LEDs", SCREEN.u(70))
    SCREEN.show()

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
def draw_text(text, y_start):
    screen_width = SCREEN.width
    if SCREEN.k > 1:
        # Marge pour rester dans le cercle de l'écran rond
        screen_width -= SCREEN.u(10)
    char_width = 8 * SCREEN.k
    line_height = 8 * SCREEN.k
    text = normalize_text(text)
    words = text.split(" ")
    line = ""
    y = y_start
    for word in words:
        if len(line + word) * char_width > screen_width:
            x = (SCREEN.width - len(line.rstrip())*char_width) // 2
            SCREEN.text(line.rstrip(), (x, y), scale=SCREEN.k)
            y += line_height
            line = word + " "
        else:
            line += word + " "
    # Affiche la dernière ligne
    x = (SCREEN.width - len(line.rstrip())*char_width) // 2
    SCREEN.text(line.rstrip(), (x, y), scale=SCREEN.k)

while True:
    blink_led(led_red, "Rouge")
    blink_led(led_green, "Vert")
    blink_led(led_blue, "Bleu")

    blink_two_leds(led_red, led_green, "Rouge", "Vert")
    blink_two_leds(led_red, led_blue, "Rouge", "Bleu")
    blink_two_leds(led_green, led_blue, "Vert", "Bleu")

    blink_all_leds()

