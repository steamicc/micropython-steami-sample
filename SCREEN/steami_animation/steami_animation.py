import framebuf
from machine import SPI, Pin
import ssd1327
from time import sleep

# Initialisation OLED
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)

def draw_eyes(bitmap, scale=8):
    width, height = 16, 16
    buf = framebuf.FrameBuffer(bytearray(bitmap), width, height, framebuf.MONO_HLSB)

    # scaled_width = width * scale
    # scaled_height = height * scale
    # scaled_bitmap = bytearray((scaled_width * scaled_height) // 8)
    # scaled_buf = framebuf.FrameBuffer(scaled_bitmap, scaled_width, scaled_height, framebuf.MONO_HLSB)

    # # Scaling
    # for y in range(height):
    #     for x in range(width):
    #         if buf.pixel(x, y):
    #             scaled_buf.fill_rect(x*scale, y*scale, scale, scale, 1)

    display.fill(0)
    # Centrage exact sur 128x128
    x_offset = (128 - width) // 2
    y_offset = (128 - height) // 2
    display.framebuf.blit(buf, x_offset, y_offset)
    display.show()

# 3 états de l’œil pour clignement
eye_open = [
    0b00000000,0b00000000,
    0b00111111,0b10000000,
    0b01000000,0b01000000,
    0b10011001,0b10010000,
    0b10100101,0b01010000,
    0b10000001,0b10000000,
    0b01000000,0b01000000,
    0b00111111,0b10000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
]

eye_half = [
    0b00000000,0b00000000,
    0b00111111,0b10000000,
    0b01000000,0b01000000,
    0b10000001,0b10010000,
    0b10111101,0b01010000,
    0b10000001,0b10000000,
    0b01000000,0b01000000,
    0b00111111,0b10000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
]

eye_closed = [
    0b00000000,0b00000000,
    0b00111111,0b10000000,
    0b01000000,0b01000000,
    0b10000000,0b00010000,
    0b10111111,0b11010000,
    0b10000000,0b00000000,
    0b01000000,0b01000000,
    0b00111111,0b10000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
    0b00000000,0b00000000,
]

# Animation clignement
states = [eye_open, eye_half, eye_closed, eye_half, eye_open]

while True:
    for state in states:
        draw_eyes(state, scale=8)
        sleep(0.2)
