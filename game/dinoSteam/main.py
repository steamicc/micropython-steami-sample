import asyncio
import framebuf
from pins import *

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

# Framebuffers
STeaMi_buf = framebuf.FrameBuffer(STeaMi_bitmap, 8, 11, framebuf.MONO_HLSB)
Cactus_buf = framebuf.FrameBuffer(Cactus_bitmap, 8, 6, framebuf.MONO_HLSB)

# Boutons
A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

# Constantes
GROUND_Y = 78
STeaMi_X = 20
JUMP_SMALL = -5
JUMP_BIG = -6

# Fonctions d'affichage
def draw_background():
    display.fill(0)
    display.framebuf.line(0, 90, 128, 90, 255)

def draw_STeaMi(x, y):
    # s'assurer que blit reçoit des entiers
    display.framebuf.blit(STeaMi_buf, int(x), int(y))

def draw_Cactus(x):
    # cast en int pour éviter TypeError si x est float
    display.framebuf.blit(Cactus_buf, int(x), 90 - 6)

async def wait_for_button(button):
    while button.value() != 0:
        await asyncio.sleep(0.02)

async def menu_screen():
    display.fill(0)
    display.framebuf.text("Dino Steam", 25, 40, 255)
    display.framebuf.text("Menu to start", 10, 70, 50)
    display.framebuf.text("A/B to jump", 18, 80, 50)
    display.show()
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
        display.framebuf.text("{}".format(points), 64, 100, 255)

        # Collision (utiliser int pour comparer correctement)
        cactus_x = int(pos_cactus)
        if (STeaMi_X + 8 > cactus_x and STeaMi_X < cactus_x + 5) and (y_steami > 70):
            return points  # Meurt => retourne le score

        # Pause menu
        if MENU_BUTTON.value() == 0:
            while MENU_BUTTON.value() == 0:
                await asyncio.sleep(0.02)
            display.framebuf.text("Pause", 40, 40, 255)
            display.show()
            while MENU_BUTTON.value() == 1:
                await asyncio.sleep(0.02)
            while MENU_BUTTON.value() == 0:
                await asyncio.sleep(0.02)

        display.show()
        await asyncio.sleep(0.02)  # tu peux réduire cette valeur pour accélérer globalement

async def game_over_screen(points):
    display.fill(0)
    display.framebuf.text("GAME OVER!", 25, 40, 255)
    display.framebuf.text("Score: {}".format(points), 30, 60, 255)
    display.framebuf.text("Menu to restart", 5, 80, 50)
    display.show()
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
