import os
os.environ["BLINKA_FT232H"] = "1"

import time
import digitalio
import board

led = digitalio.DigitalInOut(board.D7)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    print("ON")
    time.sleep(1)
    led.value = False
    time.sleep(1)
