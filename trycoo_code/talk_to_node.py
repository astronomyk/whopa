import serial
import sys
import time

# Command options: F (forward), B (backward), S (stop), R (read only)
command = sys.argv[1].upper() if len(sys.argv) > 1 else 'R'

with serial.Serial('/dev/ttyUSB0', 9600, timeout=2) as ser:
    time.sleep(1.5)  # wait for connection to settle
    if command in ['F', 'B', 'S']:
        ser.write(command.encode())
        time.sleep(0.1)

    # read response
    line = ser.readline().decode().strip()
    if line:
        print("Sensor Data:", line)
    else:
        print("No data received.")

