import os
os.environ["BLINKA_FT232H"] = "1"

import time
import digitalio
import board

in1 = digitalio.DigitalInOut(board.C0)
in1.direction = digitalio.Direction.OUTPUT

in2 = digitalio.DigitalInOut(board.C1)
in2.direction = digitalio.Direction.OUTPUT

print("FORWARD")
in2.value = False
in1.value = True
time.sleep(5)

print("REVERSE")
in1.value = False
in2.value = True
time.sleep(5)

in1.value = False
in2.value = False
