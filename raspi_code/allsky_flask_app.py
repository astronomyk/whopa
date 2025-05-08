from flask import Flask, send_file, request
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path
from picamera2 import Picamera2
import time
import numpy as np
from astropy.io import fits

app = Flask(__name__)


def capture_fits_bytes(exposure_sec=5, gain=1.0):
    exposure_us = int(exposure_sec * 1e6)

    picam2 = Picamera2()
    config = picam2.create_still_configuration(raw={"size": (1920, 1080)})
    picam2.configure(config)
    picam2.set_controls({
        "ExposureTime": exposure_us,
        "AnalogueGain": gain,
        "AeEnable": False
    })
    picam2.start()
    time.sleep(exposure_sec + 1)

    req = picam2.capture_request()
    raw = req.make_array("raw")
    hdu = fits.PrimaryHDU(raw.astype(np.uint16))

    memfile = BytesIO()
    hdu.writeto(memfile)
    memfile.seek(0)
    req.release()
    return memfile


@app.route("/capture", methods=["GET"])
def capture_endpoint():
    try:
        exposure = float(request.args.get("exposure", 5))
        gain = float(request.args.get("gain", 1.0))
        img = capture_fits_bytes(exposure, gain)
        return send_file(img, mimetype='application/fits', as_attachment=True,
                         download_name=f"allsky_{datetime.now().strftime('%Y%m%d_%H%M%S')}.fits")
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)

# This can be called on the client side with extended timeout
# response = requests.get(URL, timeout=120)  # allow long waits