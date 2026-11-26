# MicroPython LED Toggle with Buttons

This script is designed for a MicroPython environment and demonstrates how to toggle LEDs using button inputs. It uses the `pyb` module for hardware interaction.

## Features

- **LED Control**: Toggles three LEDs (red, green, and blue) based on button presses.
- **Button Inputs**: Reads input from three buttons (`A_BUTTON`, `B_BUTTON`, and `MENU_BUTTON`).
- **Debouncing**: Includes a small delay to handle button debounce.

## How It Works

1. **Pin Configuration**:
    - LEDs are configured as output pins (`LED_RED`, `LED_GREEN`, `LED_BLUE`).
    - Buttons are configured as input pins with pull-up resistors (`A_BUTTON`, `B_BUTTON`, `MENU_BUTTON`).

2. **Button Press Detection**:
    - The script continuously checks the state of the buttons.
    - When a button is pressed (value `0`), the corresponding LED toggles its state.

3. **Debounce Delay**:
    - A `sleep(0.2)` delay is added after each button press to prevent multiple toggles from a single press.

## Usage

1. Connect the LEDs and buttons to the appropriate pins on your MicroPython-compatible board.
2. Upload the script to the board.
3. Run the script. Press the buttons to toggle the LEDs.

## Example Output

When a button is pressed, the script prints a message to the console:
