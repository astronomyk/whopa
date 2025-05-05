import random
import yaml
import platform


def load_gpios_yaml(filepath="gpios.yaml"):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)


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


def get_roof_state(sensor_data, gpio_states):
    ball_switch_triggered = sensor_data.get("Ball Switch", False)

    actuator_extend_on = gpio_states.get(12, False)
    actuator_retract_on = gpio_states.get(13, False)
    actuator_moving = actuator_extend_on or actuator_retract_on

    if actuator_moving:
        return "moving"
    elif not ball_switch_triggered:
        return "open"
    else:
        return "closed"


def get_linux_temperatures():
    result = {}

    if platform.system() != "Linux":
        return result  # Temperatures only supported on Linux via psutil

    import psutil

    temps = psutil.sensors_temperatures()
    if not temps:
        return result

    for chip_name, entries in temps.items():
        chip_readings = []
        for entry in entries:
            label = entry.label or chip_name
            chip_readings.append({
                "label": label,
                "current": round(entry.current, 1),
                "high": round(entry.high, 1) if entry.high else None,
                "critical": round(entry.critical, 1) if entry.critical else None,
            })
        result[chip_name] = chip_readings

    return result
