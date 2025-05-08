import sys
from pathlib import Path
import time
from datetime import datetime, timezone
from picamera2 import Picamera2
from astropy.io import fits
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
import numpy as np

# Constants
LATITUDE = -37.303039
LONGITUDE = 144.416259
ELEVATION = 0  # meters


def debayer_RGGB(raw):
    """Debayer RGGB image to R, G, B channels."""
    r = raw[0::2, 0::2]
    g1 = raw[0::2, 1::2]
    g2 = raw[1::2, 0::2]
    b = raw[1::2, 1::2]
    g = (g1 + g2) // 2
    return r, g, b


def get_zenith_radec(timestamp):
    """Return RA/DEC in decimal degrees for zenith at given UTC datetime."""

    obs_time = Time(timestamp, scale='utc')
    location = EarthLocation(lat=LATITUDE, lon=LONGITUDE, height=ELEVATION)
    altaz = AltAz(location=location, obstime=obs_time)
    zenith = SkyCoord(alt=90 * u.deg, az=0 * u.deg, frame=altaz)
    zenith_icrs = zenith.transform_to('icrs')
    return zenith_icrs.ra.deg, zenith_icrs.dec.deg


def capture_allsky_image(exposure_time_sec, gain=1, filename_stub="allsky_image"):
    exposure_time_us = int(exposure_time_sec * 1e6)

    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (1920, 1080), "format": "BGR888"},
        raw={"size": (1920, 1080)}
    )
    picam2.configure(config)

    picam2.set_controls({
        "ExposureTime": exposure_time_us,
        "AnalogueGain": gain,
        "AeEnable": False
    })

    picam2.start()
    time.sleep(exposure_time_sec + 1.5)

    request = picam2.capture_request()
    timestamp = datetime.now(timezone.utc)
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

    raw_array = request.make_array("raw")
    r, g, b = debayer_RGGB(raw_array)

    try:
        ra, dec = get_zenith_radec(timestamp)
    except Exception:
        ra, dec = -1.0, -1.0  # fallback

    # FITS headers
    def make_hdu(data, name):
        hdu = fits.ImageHDU(data=data, name=name)
        hdu.header["DATE-OBS"] = timestamp.isoformat()
        hdu.header["EXPTIME"] = exposure_time_sec
        hdu.header["GAIN"] = gain
        hdu.header["RA"] = ra
        hdu.header["DEC"] = dec
        hdu.header["ANGLE"] = 0.0
        return hdu

    hdu_r = make_hdu(r, "RED")
    hdu_g = make_hdu(g, "GREEN")
    hdu_b = make_hdu(b, "BLUE")
    primary = fits.PrimaryHDU()
    hdul = fits.HDUList([primary, hdu_r, hdu_g, hdu_b])

    # Extract directory from filename_stub and ensure it exists
    filename_stub = Path(filename_stub)
    filename_stub.parent.mkdir(parents=True, exist_ok=True)

    fits_filename = filename_stub.with_name(f"{filename_stub.stem}_{timestamp_str}.fits")
    jpeg_filename = filename_stub.with_name(f"{filename_stub.stem}_{timestamp_str}.jpg")

    hdul.writeto(fits_filename, overwrite=True)
    request.save("main", jpeg_filename)

    request.release()
    print(f"Saved JPEG to {jpeg_filename}")
    print(f"Saved FITS to {fits_filename}")


# --- CLI Entrypoint ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python allsky_capture.py <exposure_time_sec> [gain] [filename_stub]")
        sys.exit(1)

    try:
        exposure_time_sec = float(sys.argv[1])
        gain = float(sys.argv[2]) if len(sys.argv) >= 3 else 1
        filename_stub = sys.argv[3] if len(sys.argv) >= 4 else "allsky_image"
    except ValueError:
        print("Invalid argument types. Exposure time and gain must be numbers.")
        sys.exit(1)

    capture_allsky_image(exposure_time_sec, gain, filename_stub)
