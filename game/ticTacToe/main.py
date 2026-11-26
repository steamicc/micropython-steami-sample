import asyncio
from pins import *
from math import sqrt, sin, cos, pi

# --- Constantes ---
GRID_COLS = 7
GRID_ROWS = 6
CELL_SIZE = 12  # pixels par case
CENTER_X = 64
CENTER_Y = 64
RADIUS = 64
PLAYER_CROSS = 1
PLAYER_CIRCLE = 2

# Boutons
A_BUTTON = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
B_BUTTON = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
MENU_BUTTON = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

# --- Fonctions utilitaires ---
async def wait_for_button(button):
    while button.value() != 0:
        await asyncio.sleep(0.02)

def in_circle(px, py):
    return sqrt((px - CENTER_X)**2 + (py - CENTER_Y)**2) <= RADIUS

# Coordonnées du plateau centré
OFFSET_X = (128 - GRID_COLS * CELL_SIZE) // 2
OFFSET_Y = (128 - GRID_ROWS * CELL_SIZE) // 2

def draw_cell(x, y, player):
    px = OFFSET_X + x * CELL_SIZE
    py = OFFSET_Y + y * CELL_SIZE
    if not in_circle(px + CELL_SIZE//2, py + CELL_SIZE//2):
        return
    if player == PLAYER_CROSS:
        display.framebuf.line(px, py, px + CELL_SIZE - 1, py + CELL_SIZE - 1, 255)
        display.framebuf.line(px, py + CELL_SIZE - 1, px + CELL_SIZE - 1, py, 255)
    elif player == PLAYER_CIRCLE:
        r = CELL_SIZE // 2 - 1
        cx = px + CELL_SIZE//2
        cy = py + CELL_SIZE//2
        for angle in range(0, 360, 5):
            rad = angle * pi / 180
            x1 = int(cx + r * cos(rad))
            y1 = int(cy + r * sin(rad))
            if in_circle(x1, y1):
                display.pixel(x1, y1, 255)

def draw_cursor(col):
    py_top = OFFSET_Y - 2
    py_bottom = OFFSET_Y + GRID_ROWS*CELL_SIZE + 1
    for i in range(CELL_SIZE):
        px = OFFSET_X + col * CELL_SIZE + i
        if in_circle(px, py_top):
            display.pixel(px, py_top, 255)
        if in_circle(px, py_bottom):
            display.pixel(px, py_bottom, 255)

def draw_numbers():
    # Colonnes (numéros en haut)
    for col in range(GRID_COLS):
        num = str(col+1)
        px = OFFSET_X + col * CELL_SIZE + CELL_SIZE//3
        py = OFFSET_Y - 10
        display.framebuf.text(num, px, py, 255)
    # Lignes (numéros à gauche)
    for row in range(GRID_ROWS):
        num = str(row+1)
        px = OFFSET_X - 10
        py = OFFSET_Y + row * CELL_SIZE + CELL_SIZE//3
        display.framebuf.text(num, px, py, 255)

def check_winner(board):
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            player = board[y][x]
            if player == 0:
                continue
            # Horizontal
            if x + 3 < GRID_COLS and all(board[y][x+i]==player for i in range(4)):
                return player
            # Vertical
            if y + 3 < GRID_ROWS and all(board[y+i][x]==player for i in range(4)):
                return player
            # Diagonale \
            if x + 3 < GRID_COLS and y + 3 < GRID_ROWS and all(board[y+i][x+i]==player for i in range(4)):
                return player
            # Diagonale /
            if x + 3 < GRID_COLS and y - 3 >= 0 and all(board[y-i][x+i]==player for i in range(4)):
                return player
    return 0

# --- Jeu ---
async def game_screen():
    board = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    current_player = PLAYER_CROSS
    cursor_col = 0
    winner = 0

    while not winner:
        display.fill(0)

        # Affiche le plateau et les numéros
        draw_numbers()
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                draw_cell(x, y, board[y][x])

        # Affiche le curseur
        draw_cursor(cursor_col)

        display.show()
        await asyncio.sleep(0.05)

        # Lecture boutons
        if A_BUTTON.value() == 0:
            cursor_col = (cursor_col + 1) % GRID_COLS
            await asyncio.sleep(0.2)
        if B_BUTTON.value() == 0:
            cursor_col = (cursor_col - 1) % GRID_COLS
            await asyncio.sleep(0.2)
        if MENU_BUTTON.value() == 0:
            # Pose le jeton
            for y in range(GRID_ROWS-1, -1, -1):
                if board[y][cursor_col] == 0:
                    board[y][cursor_col] = current_player
                    break
            winner = check_winner(board)
            current_player = PLAYER_CIRCLE if current_player == PLAYER_CROSS else PLAYER_CROSS
            await asyncio.sleep(0.2)

    return winner

async def game_over_screen(winner):
    display.fill(0)
    if winner == PLAYER_CROSS:
        display.framebuf.text("Cross Wins!", 20, 50, 255)
    else:
        display.framebuf.text("Circle Wins!", 20, 50, 255)
    display.framebuf.text("MENU to restart", 5, 70, 200)
    display.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)

async def menu_screen():
    display.fill(0)
    display.framebuf.text("Puissance 4", 20, 40, 255)
    display.framebuf.text("MENU to start", 10, 70, 200)
    display.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)

async def main():
    await menu_screen()
    while True:
        winner = await game_screen()
        await game_over_screen(winner)

try:
    asyncio.run(main())
except Exception as e:
    print("Erreur:", e)
    raise
