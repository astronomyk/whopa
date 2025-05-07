from sys import argv
import subprocess
import math
from datetime import datetime

PICO_ADDR = "/dev/ttyACM"
SENSOR_PORT = 0
SWITCH_PORT = 1


def set_switch_device_action(device, action, port=SWITCH_PORT):
    device = device.capitalize()  # Normalize: fan → Fan, etc.

    # Normalize shorthand numeric actions
    action_map = {
        "Lights": {
            "+1": "on",
            "1": "on",
            "0": "off",
            "-1": "off"
        },
        "Actuator": {
            "+1": "extend",
            "1": "extend",
            "-1": "retract",
            "0": "off",
        },
        "Fan": {
            "+1": "blow",
            "1": "blow",
            "-1": "suck",
            "0": "off"
        }
    }

    # Convert numeric or alias actions
    action = str(action).lower()
    if device in action_map and action in action_map[device]:
        action = action_map[device][action]

    print(f"Sending command: {device} → {action}")

    cmd = [
        "mpremote", "connect", PICO_ADDR+str(port),
        "exec", f"device='{device}'; action='{action}'; exec(open('pico_switches_action.py').read())"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout.strip())

        def log_actuator_command(device, action):
            if device.lower() != "actuator":
                return
            with open("/home/ingo/WHOPA/actuator_log.txt", "a") as f:
                f.write(f"{datetime.now().isoformat()} {action}\n")

        log_actuator_command(device, action)

    except subprocess.CalledProcessError as e:
        print("❌ Error running command:")
        print(e.stderr or e.output)


def get_switch_gpio_status(port=SWITCH_PORT):
    try:
        result = subprocess.run(
            [
                "mpremote", "connect", PICO_ADDR+str(port),
                "exec", "exec(open('pico_switches_status.py').read())"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()

        # Example: "15=0,26=1,27=0,28=1,29=0"
        pairs = output.split(",")
        gpio_status = {}
        for pair in pairs:
            if "=" in pair:
                gpio, val = pair.split("=")
                try:
                    gpio_status[int(gpio)] = int(val)
                except ValueError:
                    gpio_status[int(gpio)] = val  # in case of "ERR"
        print(gpio_status)
        return gpio_status

    except subprocess.CalledProcessError as e:
        print("❌ Failed to get GPIO status:")
        print(e.stderr or e.output)
        return {}


def get_sensor_values(sensor_name=None, port=SENSOR_PORT):
    """
    Executes pico_sensors.py via mpremote, optionally filtering for one sensor.
    Returns a dictionary of key=value pairs.
    """
    try:
        # Build the exec command
        port_addr = PICO_ADDR + str(port)
        if sensor_name:
            cmd = [
                "mpremote", "connect", port_addr,
                "exec", f"sensor='{sensor_name}'; exec(open('pico_sensors_status.py').read())"
            ]
        else:
            cmd = [
                "mpremote", "connect", port_addr,
                "exec", "exec(open('pico_sensors_status.py').read())"
            ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()

        # Handle 'NA' or empty result
        if not output or output == "NA":
            return {}

        # Parse key=value pairs
        return dict(item.split("=") for item in output.split(",") if "=" in item)

    except subprocess.TimeoutExpired:
        print("❌ Sensor read timed out.")
        return {}
    except Exception as e:
        print("❌ Error reading sensor:", e)
        return {}


def compute_tilt_angle(x, y, z, in_degrees=True):
    """
    Computes the tilt angle from the accelerometer vector relative to Z axis.
    Returns angle in degrees (default) or radians.
    """
    magnitude = math.sqrt(x**2 + y**2 + z**2)
    if magnitude == 0:
        return 0.0

    cos_theta = z / magnitude
    cos_theta = max(-1.0, min(1.0, cos_theta))  # Clamp to valid range

    angle_rad = math.acos(cos_theta)
    return math.degrees(angle_rad) if in_degrees else angle_rad


if __name__ == "__main__":
    import sys

    if len(argv) < 2:
        print("Usage:")
        print("  get_sensor [sensor_name] [--port=N]")
        print("  get_switch_state [--port=N]")
        print("  set_switch <device> <action> [--port=N]")
        sys.exit(1)

    cmd = argv[1]
    args = argv[2:]

    # Default ports
    port = None
    port_override = [arg for arg in args if arg.startswith("--port=")]
    if port_override:
        port = int(port_override[0].split("=")[1])
        args = [a for a in args if not a.startswith("--port=")]  # remove port arg

    if cmd == "get_sensor":
        sensor = args[0] if args else None
        p = port if port is not None else SENSOR_PORT
        values = get_sensor_values(sensor, port=p)
        for k, v in values.items():
            print(f"{k} = {v}")

    elif cmd == "get_switch_state":
        p = port if port is not None else SWITCH_PORT
        gpio_status = get_switch_gpio_status(port=p)
        for gpio, val in gpio_status.items():
            print(f"GPIO {gpio}: {val}")

    elif cmd == "set_switch":
        if len(args) < 2:
            print("Usage: set_switch <device> <action> [--port=N]")
            sys.exit(1)
        device = args[0]
        action = args[1]
        p = port if port is not None else SWITCH_PORT
        set_switch_device_action(device, action, port=p)

    else:
        print(f"Unknown command: {cmd}")
        print("Valid commands: get_sensor, get_switch_state, set_switch")
        sys.exit(1)
