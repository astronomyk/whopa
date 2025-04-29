import random
import yaml


def load_gpios_yaml(filepath="gpios.yaml"):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)


def get_mock_sensor_data():
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

def get_mock_gpio_states():
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


def get_roof_state(sensor_data, gpio_states):
    ball_switch_triggered = sensor_data.get("Ball Switch", False)

    actuator_extend_on = gpio_states.get(12, False)
    actuator_retract_on = gpio_states.get(13, False)
    actuator_moving = actuator_extend_on or actuator_retract_on

    if actuator_moving:
        return "half"
    elif not ball_switch_triggered:
        return "open"
    else:
        return "closed"
