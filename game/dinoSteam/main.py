import asyncio
from pins import *
from steami_screen import DARK, GREEN, WHITE

# Bitmaps
STeaMi_bitmap = bytearray([
    0b00111100,
    0b01111110,
    0b11111111,
    0b11011101,
    0b10101010,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
    0b01111110,
    0b11111111,
])

Cactus_bitmap = bytearray([
    0b00100000,
    0b00101000,
    0b10111000,
    0b11100000,
    0b00100000,
    0b00100000,
])

# Boutons
A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

# Constantes
GROUND_Y = 78
STeaMi_X = 20
JUMP_SMALL = -5
JUMP_BIG = -6

# Mise à l'échelle : le jeu calcule en unités de 128 px, SCREEN.u() les
# convertit en pixels réels. Un pixel de sprite fait SCREEN.k pixels de côté
# (1 sur 128 px, 2 sur l'écran rond de 240 px).
PIX = SCREEN.k
GROUND_PX = SCREEN.u(90)  # ligne du sol, en pixels réels

# Fonctions d'affichage
def draw_bitmap(bitmap, x, y, color):
    # chaque bit à 1 devient un carré de PIX x PIX pixels
    for row, byte in enumerate(bitmap):
        for col in range(8):
            if byte & (0x80 >> col):
                SCREEN.rect(x + col * PIX, y + row * PIX, PIX, PIX, color, fill=True)

def draw_background():
    SCREEN.clear()
    SCREEN.rect(0, GROUND_PX, SCREEN.width, PIX, WHITE, fill=True)

def draw_STeaMi(x, y):
    # x, y en unités de 128 px ; le bas du sprite garde sa hauteur au-dessus du sol
    py = GROUND_PX - SCREEN.u(90 - len(STeaMi_bitmap) - y) - len(STeaMi_bitmap) * PIX
    draw_bitmap(STeaMi_bitmap, SCREEN.u(x), py, WHITE)

def draw_Cactus(x):
    # x en unités de 128 px (float accepté : SCREEN.u() rend un entier)
    draw_bitmap(Cactus_bitmap, SCREEN.u(x), GROUND_PX - len(Cactus_bitmap) * PIX, GREEN)

async def wait_for_button(button):
    while button.value() != 0:
        await asyncio.sleep(0.02)

async def menu_screen():
    SCREEN.clear()
    SCREEN.text("Dino Steam", "CENTER", WHITE)
    SCREEN.subtitle("Menu to start", "A/B to jump", color=DARK)
    SCREEN.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)  # Anti double appui

async def game_screen():
    pos_cactus = 120.0      # float pour vitesse décimale
    y_steami = GROUND_Y
    y_velocity = 0.0
    points = 0

    # Variables dynamiques
    cactus_speed = 1.0      # pixels par frame (float ok)
    gravity = 0.5

    # limites
    MAX_CACTUS_SPEED = 6.0
    SPEED_INCREMENT = 0.15
    MAX_GRAVITY = 1.5
    MIN_POS = -10

    while True:
        draw_background()

        # Déplacement cactus (float)
        pos_cactus -= cactus_speed
        if pos_cactus < MIN_POS:
            pos_cactus = 128.0
            points += 1

            # Accélération progressive + lissage
            cactus_speed = min(cactus_speed + SPEED_INCREMENT, MAX_CACTUS_SPEED)
            gravity = min(gravity + 0.02, MAX_GRAVITY)

        # Affiche cactus (cast à l'affichage)
        draw_Cactus(pos_cactus)

        # Gestion saut
        if A_BUTTON.value() == 0 and y_steami == GROUND_Y:
            y_velocity = JUMP_SMALL
        if B_BUTTON.value() == 0 and y_steami == GROUND_Y:
            y_velocity = JUMP_BIG

        # Gravité
        y_steami += y_velocity
        y_velocity += gravity

        if y_steami > GROUND_Y:
            y_steami = GROUND_Y
            y_velocity = 0.0

        draw_STeaMi(STeaMi_X, int(y_steami))

        # Afficher le score
        SCREEN.text("{}".format(points), "S", WHITE)

        # Collision (utiliser int pour comparer correctement)
        cactus_x = int(pos_cactus)
        if (STeaMi_X + 8 > cactus_x and STeaMi_X < cactus_x + 5) and (y_steami > 70):
            return points  # Meurt => retourne le score

        # Pause menu
        if MENU_BUTTON.value() == 0:
            while MENU_BUTTON.value() == 0:
                await asyncio.sleep(0.02)
            SCREEN.text("Pause", "N", WHITE)
            SCREEN.show()
            while MENU_BUTTON.value() == 1:
                await asyncio.sleep(0.02)
            while MENU_BUTTON.value() == 0:
                await asyncio.sleep(0.02)

        SCREEN.show()
        await asyncio.sleep(0.02)  # tu peux réduire cette valeur pour accélérer globalement

async def game_over_screen(points):
    SCREEN.clear()
    SCREEN.text("GAME OVER!", "N", WHITE)
    SCREEN.text("Score: {}".format(points), "CENTER", WHITE)
    # 15 caractères ne tiennent pas sur une ligne de l'écran rond de 240 px
    SCREEN.subtitle("Menu to", "restart", color=DARK)
    SCREEN.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)  # Anti double appui

async def main():
    await menu_screen()
    while True:
        score = await game_screen()
        await game_over_screen(score)

# Lancer le jeu
try:
    asyncio.run(main())
except Exception as e:
    # Affiche l'erreur sur le REPL pour debug
    print("Erreur:", e)
    raise
