import asyncio
import framebuf
import random
from math import sqrt
from pins import *

# Constantes
GRID_SIZE = 4 # taille d'une case
CENTER_X = 64
CENTER_Y = 64
RADIUS = 64  # rayon du cercle
GRID_WIDTH = 128 // GRID_SIZE
GRID_HEIGHT = 128 // GRID_SIZE

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
def draw_cell(x, y, color=255):
    px = x * GRID_SIZE + GRID_SIZE//2
    py = y * GRID_SIZE + GRID_SIZE//2
    if sqrt((px - CENTER_X)**2 + (py - CENTER_Y)**2) <= RADIUS:
        display.framebuf.fill_rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE, color)

# Vérifie si la case est dans le cercle
def in_circle(x, y):
    px = x * GRID_SIZE + GRID_SIZE//2
    py = y * GRID_SIZE + GRID_SIZE//2
    return sqrt((px - CENTER_X)**2 + (py - CENTER_Y)**2) <= RADIUS

# Ecran de menu
async def menu_screen():
    display.fill(0)
    display.framebuf.text("SNAKE CIRCLE", 20, 40, 255)
    display.framebuf.text("Menu to start", 15, 70, 200)
    display.framebuf.text("A/B to move", 20, 85, 200)
    display.show()
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
        display.fill(0)

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

        # Dessine serpent
        for (x, y) in snake:
            draw_cell(x, y, 255)

        # Dessine pomme
        draw_cell(food[0], food[1], 150)

        # Score
        display.framebuf.text("{}".format(score), 2, 120, 255)

        display.show()
        await asyncio.sleep(0.15)  # vitesse du jeu

async def game_over_screen(score):
    display.fill(0)
    display.framebuf.text("GAME OVER", 25, 40, 255)
    display.framebuf.text("Score: {}".format(score), 30, 60, 255)
    display.framebuf.text("Menu to restart", 5, 80, 200)
    display.show()
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
