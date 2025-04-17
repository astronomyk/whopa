import sys
import time
import serial

# === Config ===
SERIAL_PORT = '/dev/ttyUSB0'  # Change if needed
BAUD_RATE = 9600

def send_command(command):
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)  # Let NodeMCU reset
        ser.write((command + '\n').encode())
        response = ser.readline().decode().strip()
        ser.close()
        return response
    except serial.SerialException as e:
        return f"ERR,SerialError: {e}"

def parse_response(response):
    parts = response.split(',')

    if parts[0] == "BMP":
        print(f"📟 BMP280 → Temp: {parts[1]} °C, Pressure: {parts[2]} hPa")
    elif parts[0] == "GYRO":
        print(f"🧭 GY-521  → Accel X:{parts[1]} Y:{parts[2]} Z:{parts[3]}")
    elif parts[0] == "DHT":
        print(f"🌡️  DHT22  → Temp: {parts[1]} °C, Humidity: {parts[2]} %")
    elif parts[0] == "MOTOR":
        print(f"⚙️  Motor Status → {parts[1]}")
    elif parts[0] == "ERR":
        print("⚠️ Error:", parts[1] if len(parts) > 1 else response)
    else:
        print("❓ Unknown response:", response)

def print_help():
    print("Usage:")
    print("  python nodemcu_controller.py [command]")
    print("\nCommands:")
    print("  read_bmp      → Get BMP280 readings")
    print("  read_gyro     → Get MPU6050 readings")
    print("  read_dht      → Get DHT22 readings")
    print("  motor_fwd     → Spin motor forward")
    print("  motor_rev     → Spin motor in reverse")
    print("  motor_stop    → Stop motor")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1]
    response = send_command(cmd)
    parse_response(response)
