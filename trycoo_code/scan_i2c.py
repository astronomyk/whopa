from pyftdi.i2c import I2cController

i2c = I2cController()
i2c.configure('ftdi://ftdi:232h/1')

print("Scanning I2C bus for devices...")
found = []

for address in range(0x03, 0x78):  # Skip reserved addresses
    try:
        slave = i2c.get_port(address)
        slave.read(1)  # Try to read 1 byte
        print(f"Found device at address 0x{address:02X}")
        found.append(address)
    except Exception:
        continue

if not found:
    print("No I2C devices found.")
