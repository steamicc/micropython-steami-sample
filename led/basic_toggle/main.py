import pyb 
from time import sleep 

led_red = pyb.LED(1)
led_green = pyb.LED(2)
led_blue = pyb.LED(3)
delay = 0.5 

led_blue.on()
sleep(delay)
led_blue.off()

led_red.on()
sleep(delay)
led_red.off()

led_green.on()
sleep(delay)
led_green.off()