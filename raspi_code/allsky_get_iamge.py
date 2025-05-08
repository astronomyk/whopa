from picamera2 import Picamera2
import time
from datetime import datetime
from astropy.io import fits
import numpy as np

# Init camera
picam2 = Picamera2()

# Create config with raw stream
config = picam2.create_still_configuration(
    main={"size": (1920, 1080), "format": "BGR888"},
    raw={"size": (1920, 1080)}
)
picam2.configure(config)

# Manual exposure
picam2.set_controls({
    "ExposureTime": 5000000,
    "AnalogueGain": 4.0,
    "AeEnable": False
})

picam2.start()
time.sleep(6)

# Timestamp filenames
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
jpeg_file = f"allsky_{timestamp}.jpg"
fits_file = f"allsky_{timestamp}.fits"

# Capture both JPEG and raw *from same frame*
raw_data = picam2.capture_file({ "main": jpeg_file, "raw": None })  # capture raw in memory

# Get raw image as numpy array
raw_array = picam2.capture_array("raw")

# Save as FITS using astropy
hdu = fits.PrimaryHDU(raw_array)
hdu.writeto(fits_file, overwrite=True)

print(f"Saved JPEG to {jpeg_file} and FITS to {fits_file}")
