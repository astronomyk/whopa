import serial
import time
import sys
import serial.tools.list_ports


# === Config ===
SERIAL_PORT = '/dev/ttyUSB0'  # You can update this as needed
BAUD_RATE = 9600


def send_command(command):
    """Send a command string to the NodeMCU over serial and return the response."""
    try:
        # Check if the port exists first
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if SERIAL_PORT not in available_ports:
            return "⚠️ Error: Serial port not found (ttyUSB0 not available)"

        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)  # Wait for NodeMCU to reset

        ser.write((command + '\n').encode())
        response = ser.readline().decode().strip()
        ser.close()

        return response if response else "⚠️ No response from NodeMCU"

    except serial.SerialException as e:
        return f"⚠️ Serial error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"


def parse_response(response):
    """Optional: Pretty-print parsed response for debugging or CLI usage."""
    parts = response.split(',')

    if parts[0] == "BMP":
        return f"📟 BMP280 → Temp: {parts[1]} °C, Pressure: {parts[2]} hPa"
    elif parts[0] == "GYRO":
        return f"🧭 GY-521  → Accel X:{parts[1]} Y:{parts[2]} Z:{parts[3]}"
    elif parts[0] == "DHT":
        return f"🌡️  DHT22  → Temp: {parts[1]} °C, Humidity: {parts[2]} %"
    elif parts[0] == "MOTOR":
        return f"⚙️  Motor Status → {parts[1]}"
    elif parts[0] == "ERR":
        return f"⚠️ Error: {parts[1] if len(parts) > 1 else response}"
    else:
        return f"❓ Unknown response: {response}"


# Optional CLI usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python talk_to_node.py [command]")
        sys.exit(1)

    cmd = sys.argv[1]
    raw = send_command(cmd)
    print(parse_response(raw))
