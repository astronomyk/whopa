from machine import Pin, ADC


# Try to get sensor filter keyword
try:
    selected_sensor = sensor.lower()
except NameError:
    selected_sensor = None

result = {}

def read_switches():
    try:
        result["bump1"] = Pin(12, Pin.IN, Pin.PULL_UP).value()
        result["bump2"] = Pin(14, Pin.IN, Pin.PULL_UP).value()
        result["ball"] = Pin(15, Pin.IN, Pin.PULL_UP).value()
    except:
        result["ball"] = result["bump1"] = result["bump2"] = "ERR"

def read_dht():
    try:
        import dht
        d = dht.DHT11(Pin(29))
        d.measure()
        result["temp"] = d.temperature()
        result["hum"] = d.humidity()
    except:
        result["temp"] = result["hum"] = "NA"

def read_rain():
    try:
        result["rain"] = ADC(Pin(28)).read_u16()
    except:
        result["rain"] = "ERR"


# --- Minimal MPU6050 class ---
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')  # wake up

    def get_values(self):
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
        def convert(h, l): return (h << 8 | l) if h < 128 else -((~(h << 8 | l) + 1) & 0xFFFF)
        return {
            "AcX": convert(data[0], data[1]),
            "AcY": convert(data[2], data[3]),
            "AcZ": convert(data[4], data[5])
        }


def read_accel():
    try:
        from machine import I2C
        i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400_000)
        imu = MPU6050(i2c)
        vals = imu.get_values()
        result["accel_x"] = vals["AcX"]
        result["accel_y"] = vals["AcY"]
        result["accel_z"] = vals["AcZ"]
    except Exception as e:
        result["accel_x"] = result["accel_y"] = result["accel_z"] = "NA"
        print("ACCEL ERROR:", e)

# --- Run Only Requested Sensors ---

if not selected_sensor or any(key in selected_sensor for key in ["ball", "bump", "switch"]):
    read_switches()

if not selected_sensor or selected_sensor in ["temp", "hum", "dht"]:
    read_dht()

if not selected_sensor or "rain" in selected_sensor:
    read_rain()

if not selected_sensor or "accel" in selected_sensor:
    read_accel()

# --- Output ---

if selected_sensor:
    filtered = {k: v for k, v in result.items() if selected_sensor in k}
    print(",".join(f"{k}={v}" for k, v in filtered.items()) if filtered else "NA")
else:
    print(",".join(f"{k}={v}" for k, v in result.items()))
