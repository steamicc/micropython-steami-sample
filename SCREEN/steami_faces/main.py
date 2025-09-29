import framebuf
from machine import SPI, Pin
import ssd1327
from time import sleep
from math import sqrt

# Initialisation de l'affichage
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")

display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

# Paramètres de mise à l'échelle
R = 64  # rayon du cercle de l'écran
char_pixels = 8 # Taille d'un pixel
factor = int((R * sqrt(2)) // char_pixels) # Calcul du facteur de mise à l'échelle
scaled_size = char_pixels * factor  # taille finale du smiley

Smileys = {
    "Eye_hatHat": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000010,
        0b10100101,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    "Eye_heart": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b10100101,
        0b11100111,
        0b01000010,
        0b00000000,
        0b00000000,
    ],
    "Eye_cross": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b10100101,
        0b01000010,
        0b10100101,
        0b00000000,
        0b00000000,
    ],
    "Eye_close": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b11100111,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    "Eye_big": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b11100111,
        0b11100111,
        0b11100111,
        0b00000000,
        0b00000000,
    ],
    "Eye_scare": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b11100111,
        0b10100101,
        0b11100111,
        0b00000000,
        0b00000000,
    ],
    "Eye_small": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000010,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    "Eye_long": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    "Eye_pissed": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b11100111,
        0b01000010,
        0b00000000,
        0b00000000,
        0b00000000,
    ],
    "Eye_cry": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b11100111,
        0b01000010,
        0b01000010,
        0b01000010,
        0b00000000,
    ],
    "Eye_sideHat": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b10000001,
        0b01000010,
        0b10000001,
        0b00000000,
        0b00000000,
    ],
    "Faces_happy": [
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b01000010,
        0b00111100,
        0b00000000,
    ],
    "Faces_neutral": [
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b00000000,
        0b01111110,
        0b00000000,
    ],
    "Faces_sad": [
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b00111100,
        0b01000010,
        0b00000000,
    ],
    "Faces_schocked": [
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b00111100,
        0b01111110,
        0b00000000,
    ],
    "Faces_bigSmile": [
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b01111110,
        0b00111100,
        0b00000000,
    ],
    "Faces_wink": [
        0b00000000,
        0b00000000,
        0b01000000,
        0b01000011,
        0b00000000,
        0b00000010,
        0b00000100,
        0b00111000,
    ],
    "Faces_cry": [
        0b00000000,
        0b00000000,
        0b11000011,
        0b01000010,
        0b01000010,
        0b00011000,
        0b00100100,
        0b00000000,
    ],
    "Faces_tongue": [
        0b00000000,
        0b00000000,
        0b01000010,
        0b01000010,
        0b00000000,
        0b01111110,
        0b00011000,
        0b00011000,
    ],
    "small_heart": [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00100100,
        0b00111100,
        0b00011000,
        0b00000000,
        0b00000000,
    ],
}

for smiley_name, bitmap in Smileys.items():
    print(f"-> {smiley_name}")
    
    bitmap_bytearray = bytearray(bitmap)
    STeaMi_buf = framebuf.FrameBuffer(bitmap_bytearray, 8, 8, framebuf.MONO_HLSB)

    scaled_bitmap = bytearray((scaled_size * scaled_size) // 8)
    scaled_buf = framebuf.FrameBuffer(scaled_bitmap, scaled_size, scaled_size, framebuf.MONO_HLSB)

    # Scaling
    for y in range(8):
        for x in range(8):
            if STeaMi_buf.pixel(x, y):
                scaled_buf.fill_rect(x * factor, y * factor, factor, factor, 1)

    # Affichage
    display.fill(0)
    x_offset = (128 - scaled_size) // 2
    y_offset = (128 - scaled_size) // 2
    display.framebuf.blit(scaled_buf, x_offset, y_offset)
    display.show()

    sleep(2)
