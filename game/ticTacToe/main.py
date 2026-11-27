import asyncio
from pins import *
from math import sqrt
from steami_screen import BLACK, LIGHT, RED, WHITE, YELLOW

# --- Constantes ---
GRID_COLS = 7
GRID_ROWS = 6
CELL_SIZE = SCREEN.u(12)  # pixels par case (12 sur 128 px, 22 sur 240 px)
CENTER_X, CENTER_Y = SCREEN.center
RADIUS = SCREEN.radius
STROKE = SCREEN.k  # épaisseur des traits : 1 sur 128 px, 2 sur 240 px
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
OFFSET_X = (SCREEN.width - GRID_COLS * CELL_SIZE) // 2
OFFSET_Y = (SCREEN.height - GRID_ROWS * CELL_SIZE) // 2

def draw_cell(x, y, player):
    px = OFFSET_X + x * CELL_SIZE
    py = OFFSET_Y + y * CELL_SIZE
    if not in_circle(px + CELL_SIZE//2, py + CELL_SIZE//2):
        return
    end = CELL_SIZE - 1
    if player == PLAYER_CROSS:
        # STROKE diagonales parallèles, dans la case
        for d in range(STROKE):
            SCREEN.line(px + d, py, px + end, py + end - d, RED)
            SCREEN.line(px + d, py + end, px + end, py + d, RED)
    elif player == PLAYER_CIRCLE:
        # anneau de STROKE pixels : disque plein, puis son intérieur effacé
        r = CELL_SIZE // 2 - 1
        cx = px + CELL_SIZE//2
        cy = py + CELL_SIZE//2
        SCREEN.circle(cx, cy, r, YELLOW, fill=True)
        SCREEN.circle(cx, cy, r - STROKE, BLACK, fill=True)

def draw_cursor(col):
    py_top = OFFSET_Y - SCREEN.u(2)
    py_bottom = OFFSET_Y + GRID_ROWS*CELL_SIZE + SCREEN.u(1)
    for i in range(CELL_SIZE):
        px = OFFSET_X + col * CELL_SIZE + i
        # traits de STROKE pixels : vers le haut au-dessus du plateau,
        # vers le bas en dessous
        if in_circle(px, py_top):
            SCREEN.rect(px, py_top - STROKE + 1, 1, STROKE, WHITE, fill=True)
        if in_circle(px, py_bottom):
            SCREEN.rect(px, py_bottom, 1, STROKE, WHITE, fill=True)

def draw_numbers():
    # Chiffres de 8 x SCREEN.k pixels, centrés sur leur case
    digit = 8 * SCREEN.k
    # Colonnes (numéros en haut)
    for col in range(GRID_COLS):
        num = str(col+1)
        px = OFFSET_X + col * CELL_SIZE + (CELL_SIZE - digit) // 2
        py = OFFSET_Y - SCREEN.u(10) - STROKE + 1  # au-dessus du curseur
        SCREEN.text(num, (px, py), WHITE, scale=SCREEN.k)
    # Lignes (numéros à gauche)
    for row in range(GRID_ROWS):
        num = str(row+1)
        px = OFFSET_X - SCREEN.u(10)
        py = OFFSET_Y + row * CELL_SIZE + (CELL_SIZE - digit) // 2
        SCREEN.text(num, (px, py), WHITE, scale=SCREEN.k)

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
        SCREEN.clear()

        # Affiche le plateau et les numéros
        draw_numbers()
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                draw_cell(x, y, board[y][x])

        # Affiche le curseur
        draw_cursor(cursor_col)

        SCREEN.show()
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
    SCREEN.clear()
    if winner == PLAYER_CROSS:
        SCREEN.text("Cross Wins!", "CENTER", WHITE)
    else:
        SCREEN.text("Circle Wins!", "CENTER", WHITE)
    # 15 caractères ne tiennent pas sur une ligne de l'écran rond de 240 px
    SCREEN.subtitle("MENU to", "restart", color=LIGHT)
    SCREEN.show()
    await wait_for_button(MENU_BUTTON)
    await asyncio.sleep(0.2)

async def menu_screen():
    SCREEN.clear()
    SCREEN.text("Puissance 4", "CENTER", WHITE)
    SCREEN.subtitle("MENU to start", color=LIGHT)
    SCREEN.show()
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
