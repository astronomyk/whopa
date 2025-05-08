from picamera2 import Picamera2
import time

picam2 = Picamera2()

# Create a high-resolution still configuration
config = picam2.create_still_configuration(
    main={"size": (1920, 1080)},  # Full sensor resolution
    raw={"size": (1920, 1080)}
)
picam2.configure(config)

# Set manual controls (example: 5 seconds exposure)
picam2.set_controls({
    "ExposureTime": 5000000,  # in microseconds (5 seconds)
    "AnalogueGain": 4.0,
    "AeEnable": False
})

picam2.start()
time.sleep(6)  # Let the sensor expose (longer than exposure time)
picam2.capture_file("allsky_image.jpg")
