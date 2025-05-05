import platform
from utils_picos import get_sensor_values, get_switch_gpio_status
import yaml
import psutil


def load_gpios_yaml(filepath="gpios.yaml"):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)


def get_sensor_data():
    raw = get_sensor_values()

    # Normalize and convert
    data = {
        "Ball Switch": "Closed" if raw.get("Ball", "0") == "1" else "Open",
        "Bump Switch 1": "Closed" if raw.get("Bump1", "0") == "1" else "Open",
        "Bump Switch 2": "Closed" if raw.get("Bump2", "0") == "1" else "Open",
        "GY-521": {
            "d2x": float(raw.get("d2x", 0)),
            "d2y": float(raw.get("d2y", 0)),
            "d2z": float(raw.get("d2z", 0)),
            "Temp": float(raw.get("d2temp", 0))
        },
        "Rain": float(raw.get("Rain", 0)),
        "DHT11": {
            "Temp": float(raw.get("dht_temp", 0)),
            "Humidity": float(raw.get("dht_hum", 0))
        }
    }

    return data


def get_gpio_states():
    """
    Returns GPIO status as {pin: bool}
    """
    raw_states = get_switch_gpio_status()
    return {pin: (val == 1) for pin, val in raw_states.items()}


def get_roof_state(sensor_data, gpio_states):
    """
    Infers roof state based on ball switch and GPIO outputs
    """
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
        return result  # Not supported

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
