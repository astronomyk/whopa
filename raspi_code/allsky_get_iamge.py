from picamera2 import Picamera2
import time
from datetime import datetime
from astropy.io import fits
import numpy as np

# Initialize camera
picam2 = Picamera2()

# Configure for both main and raw streams
config = picam2.create_still_configuration(
    main={"size": (1920, 1080), "format": "BGR888"},
    raw={"size": (1920, 1080)}
)
picam2.configure(config)

# Set manual exposure
picam2.set_controls({
    "ExposureTime": 5000000,
    "AnalogueGain": 4.0,
    "AeEnable": False
})

picam2.start()
time.sleep(6)

# Capture single request with both outputs
request = picam2.capture_request()
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Save JPEG
jpeg_file = f"allsky_{timestamp}.jpg"
request.save("main", jpeg_file)

# Save FITS
fits_file = f"allsky_{timestamp}.fits"
raw_array = request.make_array("raw")
hdu = fits.PrimaryHDU(raw_array)
hdu.writeto(fits_file, overwrite=True)

print(f"Saved JPEG to {jpeg_file} and FITS to {fits_file}")
request.release()
