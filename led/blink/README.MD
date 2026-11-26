# MicroPython LED Toggle with Buttons

This script is designed for a MicroPython environment and demonstrates how to toggle LEDs using button inputs. It uses the `pyb` module for hardware interaction.

## Features

- **LED Control**: Toggles three LEDs (red, green, and blue) based to the sequence.
- **Display Screen**: Display the name of the LEDs (red, green, and blue) based on which is turn on.

## How It Works

1. **Pin Configuration**:
    - LEDs are initialized as LEDs with the pyb library(Red LED -> pyb.LED(1), Green LED -> pyb.LED(2), Blue LED -> pyb.LED(3) ).
    - Screen is initialized as pins() and with a size of 128x128 (`DATA_COMMAND_DISPLAY`,`RST_DISPLAY`, `CS_DISPLAY`)

2. **Definition of functions**:
    - Defining the blink functions of one, two and all LEDs.
    - Defining text normalization function to replace accented characters with a regular character (é -> e, ô -> o, Ê -> E)
    - Defining of the line break and text centering function depending on the length of the text to be displayed

## Usage

1. Connect the LEDs and the Screen to the appropriate pins on your MicroPython-compatible board.
2. Upload the script to the board.
3. Run the script.

## Example Output

When the script is running, the script turn on and off the LEDs sequence and display the name of LED' color wich is turn on :

1. Display on the Script : "LEDs allumée(s) : LED Rouge"
2. Turn on the red LED, wait 0.5 secondes, turn off the red LED, wait 0.5 secondes
4. Display on the Script : "LEDs allumée(s) : LED Vert"
5. Turn on the green LED, wait 0.5 secondes, turn off the green LED, wait 0.5 secondes
6. Display on the Script : "LEDs allumée(s) : LED Bleue"
7. Turn on the blue LED, wait 0.5 secondes, turn off the blue LED, wait 0.5 secondes
6. Display on the Script : "LEDs allumée(s) : - LED Rouge - LED Vert"
7. Turn on the red LED, turn on the green LED, wait 0.5 secondes, turn off the red LED, turn off the green LED, wait 0.5 secondes
8. Same process for each LED lighting combination