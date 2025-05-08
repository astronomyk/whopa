from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()

# Set a custom configuration
config = picam2.create_still_configuration()
picam2.configure(config)

# Set manual exposure (in microseconds) and disable auto-exposure
picam2.set_controls({
    "ExposureTime": 5000000,  # 5 seconds
    "AnalogueGain": 1.0,
    "AeEnable": False
})

picam2.start()
time.sleep(6)  # Let the sensor integrate
picam2.capture_file("long_exposure.jpg")
