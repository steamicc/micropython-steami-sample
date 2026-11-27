import asyncio
import random
from math import sqrt
from pins import *
from steami_screen import DARK, LIGHT, RED, WHITE

# Constantes
GRID_SIZE = 4 # taille d'une case
CENTER_X = 64
CENTER_Y = 64
RADIUS = 64  # rayon du cercle
GRID_WIDTH = 128 // GRID_SIZE
GRID_HEIGHT = 128 // GRID_SIZE

# Le jeu calcule sur la grille de 128 px ; à l'écran, une case fait CELL
# pixels réels (4 sur 128 px, 7 sur l'écran rond de 240 px) et la grille
# est centrée.
CELL = SCREEN.width // GRID_WIDTH
ORIGIN_X = (SCREEN.width - GRID_WIDTH * CELL) // 2
ORIGIN_Y = (SCREEN.height - GRID_HEIGHT * CELL) // 2

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Boutons
A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

# Attendre qu'un bouton soit pressé
async def wait_for_button(button):
    while button.value() != 0:
        await asyncio.sleep(0.02)

# Dessine une case si elle est dans le cercle
def draw_cell(x, y, color=WHITE):
    px = x * GRID_SIZE + GRID_SIZE//2
    py = y * GRID_SIZE + GRID_SIZE//2
    if sqrt((px - CENTER_X)**2 + (py - CENTER_Y)**2) <= RADIUS:
        SCREEN.rect(ORIGIN_X + x * CELL, ORIGIN_Y + y * CELL, CELL, CELL, color, fill=True)

# Vérifie si la case est dans le cercle
def in_circle(x, y):
    px = x * GRID_SIZE + GRID_SIZE//2
    py = y * GRID_SIZE + GRID_SIZE//2
    return sqrt((px - CENTER_X)**2 + (py - CENTER_Y)**2) <= RADIUS

# Ecran de menu
async def menu_screen():
    SCREEN.clear()
    SCREEN.text("SNAKE CIRCLE", "CENTER", WHITE)
    SCREEN.subtitle("Menu to start", "A/B to move", color=LIGHT)
    SCREEN.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)

# Ecran de jeu
async def game_screen():
    # Initialisation du serpent
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = RIGHT

    # Génère la pomme dans le cercle
    while True:
        food = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
        )
        if in_circle(food[0], food[1]):
            break

    score = 0

    while True:
        SCREEN.clear()

        # Lecture boutons : simple mapping
        if A_BUTTON.value() == 0 and direction == DOWN:
            direction = LEFT
        elif A_BUTTON.value() == 0 and direction == LEFT:
            direction = UP
        elif A_BUTTON.value() == 0 and direction == UP:
            direction = RIGHT
        elif A_BUTTON.value() == 0 and direction == RIGHT:
            direction = DOWN
        elif B_BUTTON.value() == 0 and direction == DOWN:
            direction = RIGHT
        elif B_BUTTON.value() == 0 and direction == RIGHT:
            direction = UP
        elif B_BUTTON.value() == 0 and direction == UP:
            direction = LEFT
        elif B_BUTTON.value() == 0 and direction == LEFT:
            direction = DOWN


        # Déplacement du serpent
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Collision avec soi-même ou sortie du cercle ?
        if new_head in snake or not in_circle(new_head[0], new_head[1]):
            return score  # Game over

        # Ajout nouvelle tête
        snake.insert(0, new_head)

        # Vérifie si on mange la pomme
        if new_head == food:
            score += 1
            # Nouvelle pomme dans le cercle
            while True:
                food = (
                    random.randint(0, GRID_WIDTH - 1),
                    random.randint(0, GRID_HEIGHT - 1),
                )
                if food not in snake and in_circle(food[0], food[1]):
                    break
        else:
            # sinon, enlève la queue
            snake.pop()

        # Score (en bas, dans le cercle : tracé en premier et en gris foncé,
        # le serpent et la pomme passent par-dessus)
        SCREEN.text("{}".format(score), "S", DARK)

        # Dessine serpent
        for (x, y) in snake:
            draw_cell(x, y, WHITE)

        # Dessine pomme
        draw_cell(food[0], food[1], RED)

        SCREEN.show()
        await asyncio.sleep(0.15)  # vitesse du jeu

async def game_over_screen(score):
    SCREEN.clear()
    SCREEN.text("GAME OVER", "N", WHITE)
    SCREEN.text("Score: {}".format(score), "CENTER", WHITE)
    # 15 caractères ne tiennent pas sur une ligne de l'écran rond de 240 px
    SCREEN.subtitle("Menu to", "restart", color=LIGHT)
    SCREEN.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)

async def main():
    await menu_screen()
    while True:
        score = await game_screen()
        await game_over_screen(score)

try:
    asyncio.run(main())
except Exception as e:
    print("Erreur:", e)
    raise
