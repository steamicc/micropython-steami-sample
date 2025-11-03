# Snake Circle Game

## Overview

This project is a MicroPython-based mini game inspired by the classic "Snake". It runs on embedded hardware with an OLED display and buttons. The player controls a snake moving inside a circular boundary, trying to eat apples while avoiding collisions with itself or the circle boundary.

## Features

* Circular 128×128 grid gameplay
* Snake moves in 4 directions: up, down, left, right
* Apple randomly appears inside the circular boundary
* OLED graphics with pixel-based animation
* Live score display
* Pause and restart with the MENU button
* Game over screen with score

## Hardware Requirements

* Microcontroller compatible with MicroPython (e.g., Pyboard)
* SSD1327 OLED display (SPI)
* 3 Buttons (A, B, MENU)
* SPI pins wired for display
* No additional sensors required

## File Descriptions

* `main.py`: Game logic, rendering loop, snake movement, collision detection, and UI.
* `pins.py`: Pin configuration for the display and buttons.

## Controls

* **A Button** – Change snake direction (left/rotate)
* **B Button** – Change snake direction (right/rotate)
* **MENU Button**
  * Start game from menu
  * Pause/resume during gameplay
  * Restart after game over

## Usage

1. Flash your board with MicroPython.
2. Upload `main.py` and `pins.py`.
3. Reboot the board — the game starts with a welcome screen.
4. Press MENU to start playing.
5. Use A and B buttons to control the snake direction.
