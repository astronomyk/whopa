# pico_switches_action.py

from machine import Pin

try:
    dev = device
    act = action.lower()
except NameError:
    print("Error: 'device' and 'action' variables must be defined.")
    raise SystemExit

pin_map = {
    "Actuator": {"Retract": 15, "Extend": 26},
    "Lights": {"Lights": 27},
    "Fan": {"Blow": 28, "Suck": 29},
}

if dev not in pin_map:
    print(f"Unknown device: {dev}")
    raise SystemExit

pins = pin_map[dev]

# Lights: simple ON/OFF
if dev == "Lights":
    light_pin = Pin(pins["Lights"], Pin.OUT)
    if act == "on":
        light_pin.value(1)
    elif act == "off":
        light_pin.value(0)
    else:
        print(f"Unknown action '{act}' for Lights.")
        raise SystemExit
    print(f"Lights set to {act.upper()}")

# Fan & Actuator: dual GPIO control
else:
    names = list(pins.keys())  # e.g., ["Blow", "Suck"]
    p1 = Pin(pins[names[0]], Pin.OUT)
    p2 = Pin(pins[names[1]], Pin.OUT)

    if act == names[0].lower():  # e.g., "blow" or "extend"
        p1.value(1)
        p2.value(0)
    elif act == names[1].lower():  # e.g., "suck" or "retract"
        p1.value(0)
        p2.value(1)
    elif act == "off":
        p1.value(0)
        p2.value(0)
    else:
        print(f"Unknown action '{act}' for {dev}")
        raise SystemExit

    print(f"{dev} set to {act.upper()}")
