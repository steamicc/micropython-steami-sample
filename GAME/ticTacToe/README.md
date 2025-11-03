# Puissance 4 Circle Game

## Overview

This project is a MicroPython-based mini game inspired by classic Connect 4 (Puissance 4), adapted for a circular play area. It runs on embedded hardware with an OLED display and buttons, where two players take turns dropping tokens (crosses or circles) into a circular grid.

## Features

* 7 columns × 6 rows grid, restricted inside a circle
* Two players: Cross (X) and Circle (O)
* OLED graphics with pixel-based display
* Visual cursor to indicate the current column
* Column and row numbering for easier navigation
* Game over detection for winning combinations (horizontal, vertical, diagonal)
* Menu and restart support via MENU button

## Hardware Requirements

* Microcontroller compatible with MicroPython (e.g. Pyboard)
* SSD1327 OLED display (SPI)
* 3 Buttons (A, B, MENU)
* SPI pins wired for display
* No additional sensors required

## File Descriptions

* `main.py`: Game logic and rendering loop, including drawing, token placement, and winner detection.
* `pins.py`: Pin configuration for the display and buttons.

## Controls

* **A Button** – Move cursor right  
* **B Button** – Move cursor left  
* **MENU Button** – Place token / confirm move, also restart after game over  

## Usage

1. Flash your board with MicroPython.  
2. Upload `main.py` and `pins.py`.  
3. Reboot the board — the game starts with a welcome menu.  
4. Press MENU to start playing.  
5. Use A/B to navigate columns and MENU to drop your token.  
6. The game will indicate the winner and allow restarting with MENU.
