import random


def get_sensor_data():
    return {
        "Ball Switch": random.choice(["Open", "Closed"]),
        "Bump Switch 1": random.choice(["Open", "Closed"]),
        "Bump Switch 2": random.choice(["Open", "Closed"]),
        "GY-521": {"d2x": random.uniform(-1, 1),
                   "d2y": random.uniform(-1, 1),
                   "d2z": random.uniform(-1, 1),
                   "Temp": random.uniform(0, 60)},
        "Rain": random.uniform(0, 100),
        "DHT11": {"Temp": random.uniform(15, 25),
                  "Humidity": random.uniform(30, 70)},
    }


def get_gpio_states():
    """
    Return a mock dictionary of GPIO states (True for ON, False for OFF).
    """
    return {
        12: random.choice([True, False]),  # Actuator Extend
        13: random.choice([True, False]),  # Actuator Retract
        26: random.choice([True, False]),  # Lights
        27: random.choice([True, False]),  # Fan Blow
        28: random.choice([True, False])   # Fan Suck
    }
