# (Pin  1) 3V3     is used for all sensors
# (Pin  3) GPIO 2  is used as SDA Motion and BMP280
# (Pin  5) GPIO 3  is used as SCL Motion and BMP280
# (Pin  7) GPIO 4  is used as Serial DHT22
# (Pin  9) GND     is used for all sensors
# (Pin 11) GPIO 17 is used as Binary for Rain
# (Pin 13) GPIO 27 is used as Binary for Light
# (Pin 15) ---
# (Pin 17) 3v3     is used for all Relais-Switches
# (Pin 19) GPIO 10 is used for open Relais
# (Pin 21) GPIO 9  is used for close Relais
# (Pin 23) ---
# (Pin 25) GND     is used for all Relais-Switches
# (Pin 27) ---
# (Pin 29) ---
# (Pin 31) GPIO 6  is used for Binary Bump 1
# (Pin 33) GPIO 13 is used for Binary Bump 2
# (Pin 35) GPIO 29 is used for Binary Bump 3
# (Pin 37) GPIO 26 is used for Binary Bump 4
# (Pin 39) GND

from time import sleep

from gpiozero import DigitalInputDevice, Button
from signal import pause

from smbus2 import SMBus
from bmp280 import BMP280

import mpu6050

import board
import adafruit_dht


sensor_dict = {}

# (Pin  1) 3V3    is used for all sensors
# (Pin  3) GPIO 2 is used as SDA
# (Pin  5) GPIO 3 is used as SCL

# Get input from the I2C weather sensor
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)
sensor_dict["temp_bmp"] = bmp280.get_temperature()
sensor_dict["pressure"] = bmp280.get_pressure()

# Get input from the I2C movement sensor
mpu6050 = mpu6050.mpu6050(0x68)
sensor_dict["temp_mpu"] = mpu6050.get_temp()
sensor_dict["gyro"] = mpu6050.get_gyro_data()
sensor_dict["accel"] = mpu6050.get_accel_data()

# (Pin 7) GPIO 4 is used as Serial

# Get the input from the DHT22
try:
	pin = board.D4
	dhtDevice = adafruit_dht.DHT22(pin, use_pulseio=False)
	sensor_dict["temp_dht"] = dhtDevice.temperature
	sensor_dict["humidity"] = dhtDevice.humidity
except:
	print("DHT22 chucked a hissy-fit")

# (Pin  9) GND     is used for all sensors
# (Pin 11) GPIO 17 is used as Binary for Rain
# (Pin 13) GPIO 27 is used as Binary for Light

# Get the state of the binary rain+light sensors
rain_sensor = DigitalInputDevice(17)
light_sensor = DigitalInputDevice(27)
sensor_dict["rain"] = rain_sensor.value
sensor_dict["light"] = light_sensor.value
light_sensor.close()

# (Pin 15) ---
# (Pin 17) 3v3     is used for all Relais-Switches
# (Pin 19) GPIO 10 is used for open Relais
# (Pin 21) GPIO 9  is used for close Relais
# (Pin 23) ---
# (Pin 25) GND     is used for all Relais-Switches
# (Pin 27) --- (Reserved)
# (Pin 29) ---

# (Pin 31) GPIO 6  is used for Binary Bump 1
# (Pin 33) GPIO 13 is used for Binary Bump 2
# (Pin 35) GPIO 29 is used for Binary Bump 3
# (Pin 37) GPIO 26 is used for Binary Bump 4
# (Pin 39) --- (GND)

# Get the state of the bump-sensors
bump_1 = Button(6)
bump_2 = Button(13)
bump_3 = Button(19)
bump_4 = Button(26)
sensor_dict["bump_1"] = bump_1.value
sensor_dict["bump_2"] = bump_2.value
sensor_dict["bump_3"] = bump_3.value
sensor_dict["bump_4"] = bump_4.value
bump_1.close()
bump_2.close()
bump_3.close()
bump_4.close()


for key, value in sensor_dict.items():
	print(key, value)

