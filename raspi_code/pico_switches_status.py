# pico_switches_status.py

from machine import Pin

# Define the GPIO pins to read
pins = {
    "Actuator_Extend": 15,
    "Actuator_Retract": 26,
    "Lights": 27,
    "Fan_Blow": 28,
    "Fan_Suck": 29,
}

results = []

# Read each pin and collect results
for gpio_num in pins.values():
    try:
        pin = Pin(gpio_num, Pin.OUT)
        results.append(f"{gpio_num}={pin.value()}")
    except:
        results.append(f"{gpio_num}=ERR")

# Output one line
print(",".join(results))
