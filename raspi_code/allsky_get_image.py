import argparse
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


def capture_allsky_image(exposure_time_sec, gain=1, add_timestamp=False,
                         filename_stub="/home/ingo/allsky_output/allsky_image"):

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

    timestamp = datetime.now(timezone.utc)
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

    # Add timestamp to stem if requested
    if add_timestamp:
        base_name = f"{filename_stub.stem}_{timestamp_str}"
    else:
        base_name = filename_stub.stem

    # Rebuild full path using original parent + new name
    base = filename_stub.with_name(base_name)

    # Final file paths
    jpeg_filename = base.with_suffix(".jpg")
    fits_filename = base.with_suffix(".fits")

    request.save("main", jpeg_filename)
    hdul.writeto(fits_filename, overwrite=True)

    request.release()
    print(f"Saved JPEG to {jpeg_filename}")
    print(f"Saved FITS to {fits_filename}")


# --- CLI Entrypoint ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture all-sky image with "
                                             "Raspberry Pi and IMX462 camera.")
    parser.add_argument("exposure", type=float,
                        help="Exposure time in seconds")
    parser.add_argument("gain",
                        type=float,
                        nargs="?",
                        default=1.0,
                        help="Analog gain (default: 1)")
    parser.add_argument("filename_stub",
                        nargs="?",
                        default="/home/ingo/allsky_output/allsky_image",
                        help="Base output filename (can include path)")
    parser.add_argument("--add-timestamp", "-t",
                        action="store_true",
                        help="Append timestamp to filename")

    args = parser.parse_args()

    capture_allsky_image(exposure_time_sec=args.exposure,
                         gain=args.gain,
                         add_timestamp=args.add_timestamp,
                         filename_stub=args.filename_stub)
