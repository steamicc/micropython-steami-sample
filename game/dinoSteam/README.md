# Dino STeaMi Game

## Overview

This project is a MicroPython-based mini game inspired by the classic "Dino Run". It runs on embedded hardware with an OLED display and buttons, where the player controls a jumping character (STeaMi) to avoid incoming cacti.

## Features

* Simple endless runner gameplay
* Two jump modes (short/long) using buttons A and B
* OLED graphics with pixel-based animation
* Live score display
* Pause and restart with the MENU button
* Game over screen with score

## Hardware Requirements

* Microcontroller compatible with MicroPython (e.g. Pyboard)
* SSD1327 OLED display (SPI)
* 3 Buttons (A, B, MENU)
* SPI pins wired for display
* No additional sensors required

## File Descriptions

* `main.py`: Game logic and rendering loop, including drawing, collision detection, and UI.
* `pins.py`: Pin configuration for the display and buttons.

## Controls

* **A Button** – Short jump
* **B Button** – Long jump
* **MENU Button**

  * Start game from menu
  * Pause/resume during gameplay
  * Restart after game over

## Usage

1. Flash your board with MicroPython.
2. Upload `main.py` and `pins.py`.
3. Reboot the board — the game starts with a welcome screen.
4. Press MENU to start playing.