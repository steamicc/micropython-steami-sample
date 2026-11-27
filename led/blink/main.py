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

# Texte : cellules de 8 px de large et SCREEN.text_height() de haut (8x8 sur
# 128 px, Spleen 8x16 sur 240 px) ; une ligne toutes les hauteurs de cellule
# + 2k px (10 sur 128 px, 20 sur 240 px). Le titre est en u(50), la liste
# deux lignes plus bas.
LINE = SCREEN.text_height() + 2 * SCREEN.k
TOP = SCREEN.u(50)

# Fonctions pour faire clignoter une LED
def blink_led(led, couleur):
    SCREEN.clear()
    draw_text("LED Allumée(s)", TOP)
    draw_text(f"- LED {couleur}", TOP + 2 * LINE)
    SCREEN.show()

    led.on()
    sleep(delay)
    led.off()
    sleep(delay)

# Fonction pour faire clignoter deux LEDs
def blink_two_leds(led1, led2, couleur1, couleur2):
    SCREEN.clear()
    draw_text("LED Allumée(s)", TOP)
    draw_text(f"- LED {couleur1}", TOP + 2 * LINE)
    draw_text(f"- LED {couleur2}", TOP + 3 * LINE)
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
    draw_text("LED Allumée(s)", TOP)
    draw_text("Toutes les LEDs", TOP + 2 * LINE)
    SCREEN.show()

    led_red.on()
    led_green.on()
    led_blue.on()
    sleep(delay)
    led_red.off()
    led_green.off()
    led_blue.off()
    sleep(delay)

# Fonction pour afficher le texte avec retour à la ligne et centrage automatique.
# Les accents sont dessinés par la police Spleen sur 240 px et ramenés à la
# lettre simple par la bibliothèque sur 128 px.
def draw_text(text, y_start):
    screen_width = SCREEN.width
    if SCREEN.k > 1:
        # Marge pour rester dans le cercle de l'écran rond
        screen_width -= SCREEN.u(10)
    char_width = 8
    words = text.split(" ")
    line = ""
    y = y_start
    for word in words:
        if len(line + word) * char_width > screen_width:
            x = (SCREEN.width - len(line.rstrip())*char_width) // 2
            SCREEN.text(line.rstrip(), (x, y))
            y += LINE
            line = word + " "
        else:
            line += word + " "
    # Affiche la dernière ligne
    x = (SCREEN.width - len(line.rstrip())*char_width) // 2
    SCREEN.text(line.rstrip(), (x, y))

while True:
    blink_led(led_red, "Rouge")
    blink_led(led_green, "Vert")
    blink_led(led_blue, "Bleu")

    blink_two_leds(led_red, led_green, "Rouge", "Vert")
    blink_two_leds(led_red, led_blue, "Rouge", "Bleu")
    blink_two_leds(led_green, led_blue, "Vert", "Bleu")

    blink_all_leds()

