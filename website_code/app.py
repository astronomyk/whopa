import io
import os
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import zipfile
from pathlib import Path
from flask import Flask, request, render_template, url_for, flash, send_file, send_from_directory, redirect

from plot_wind_from_bom import plot_vic_wind_data_with_quivers
from plot_object_visibility import plot_altitude_for_seasons

from get_pico_states import get_sensor_data, get_gpio_states, get_roof_state, get_linux_temperatures, load_gpios_yaml

from utils_astro import get_sun_moon_altitudes
from utils_picos import set_switch_device_action, compute_tilt_angle
from utils_archive_data_access import build_file_tree  # import the helper
from utils_seestar_data_access import sync_fits_files_to_local, crawl_seestar  # Adjust import paths
from utils_system import start_script_if_not_running


ARCHIVE_PATH = "/media/ingo/archive"
CTL_SCRIPTS_PATH = Path(__file__).parent.parent / "control_scripts/"

# Load GPIO setup
gpios_config = load_gpios_yaml()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages

@app.route("/", methods=["GET", "POST"])
def dashboard():
    celestial = get_sun_moon_altitudes()
    return render_template("dashboard.html",
                           celestial=celestial,
                           radar_timestamp=int(datetime.utcnow().timestamp()))


@app.route("/observatory", methods=["GET", "POST"])
def observatory_page():
    sensor_data = get_sensor_data()
    gpio_states = get_gpio_states()
    roof_state = get_roof_state(sensor_data, gpio_states)
    linux_temperatures = get_linux_temperatures()

    def round_floats(obj):
        if isinstance(obj, dict):
            return {k: round_floats(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [round_floats(item) for item in obj]
        elif isinstance(obj, float):
            return round(obj, 2)
        else:
            return obj

    sensor_data = round_floats(sensor_data)

    gyro_data = sensor_data.get("GY-521", {})
    x = float(gyro_data.get("Accel_x", 0))
    y = float(gyro_data.get("Accel_y", 0))
    z = float(gyro_data.get("Accel_z", 1))
    tilt_angle = round(compute_tilt_angle(x, y, z))

    if request.method == "POST":
        # e.g., "Actuator_extend", "Lights_off"
        action = request.form.get("action")
        if action:
            try:
                device, act = action.split("_", 1)
                print(device, act, action)
                set_switch_device_action(device, act)
                flash(f"✅ Command sent: {device} → {act}")
            except Exception as e:
                flash(f"❌ Failed to send command: {e}")
        else:
            flash("⚠️ No action received.")

    return render_template("observatory.html",
                           gpios=gpios_config,
                           sensors=sensor_data,
                           gpio_states=gpio_states,
                           roof_state=roof_state,
                           tilt_angle=tilt_angle,
                           linux_temperatures=linux_temperatures)


@app.route("/telescope")
def telescope_page():
    # Option 1: embed
    return render_template("telescope.html")
    # Option 2: redirect to port 5432
    # return redirect("http://localhost:5432")


@app.route("/wind-map.png")
def wind_map():
    fig = plot_vic_wind_data_with_quivers(return_fig=True)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype='image/png')


@app.route("/refresh", methods=["POST"])
def refresh_map():
    try:
        fig = plot_vic_wind_data_with_quivers(return_fig=True)

        # Save it to disk (so index page uses the updated image)
        fig.savefig("static/wind_map.png", bbox_inches='tight')
        flash("✅ Wind map refreshed successfully.")
    except Exception as e:
        flash(f"❌ Error refreshing wind map: {e}")
    return redirect(url_for('index'))


@app.route("/visibility", methods=["GET", "POST"])
def visibility_page():
    plot_img = None
    celestial = get_sun_moon_altitudes()

    if request.method == "POST":
        object_name = request.form.get("object_name")
        try:
            buf = io.BytesIO()
            plot_altitude_for_seasons(object_name, save_path=buf)
            buf.seek(0)
            plot_img = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
        except ValueError as e:
            flash(str(e))  # This shows the "Object not found" message
        except Exception as e:
            flash(f"❌ Error plotting object: {e}")

    return render_template("dashboard.html", plot_img=plot_img, celestial=celestial)


@app.route("/files")
def files_page():
    file_tree = build_file_tree(ARCHIVE_PATH)
    return render_template("files.html", file_tree=file_tree)


@app.route("/files/<path:filepath>")
def download_file(filepath):
    return send_from_directory(ARCHIVE_PATH, filepath, as_attachment=False)


@app.route("/download_folder", methods=["POST"])
def download_folder():
    folder = request.form.get("folder_name")
    base_path = ARCHIVE_PATH  # Update to your actual folder base

    target_path = os.path.join(base_path, folder)

    if not os.path.isdir(target_path):
        flash(f"Folder '{folder}' not found.")
        return redirect(url_for("files_page"))

    # Create zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(target_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, start=base_path)
                zipf.write(abs_path, rel_path)

    zip_buffer.seek(0)
    zip_filename = f"{folder}.zip"
    return send_file(zip_buffer, mimetype='application/zip',
                     as_attachment=True, download_name=zip_filename)


@app.route("/sync_fits", methods=["POST"])
def sync_fits():
    try:
        crawl_data = crawl_seestar()  # You must define or import this
        dest_root = ARCHIVE_PATH  # Replace with your actual path

        sync_fits_files_to_local(crawl_data, dest_root)
        flash("✅ FITS files synced successfully.")
    except Exception as e:
        flash(f"❌ Sync failed: {e}")

    return redirect(url_for("files_page"))  # Or whatever the route is


@app.route("/launch_seestar")
def launch_seestar():
    start_script_if_not_running("seestar_alp", CTL_SCRIPTS_PATH / "start_seestar_alp.sh")

    host_ip = request.host.split(':')[0]
    return redirect(f"http://{host_ip}:5432")

@app.route("/launch_webcam")
def launch_webcam():
    start_script_if_not_running("mjpg_streamer", CTL_SCRIPTS_PATH / "start_webcam.sh")

    host_ip = request.host.split(':')[0]
    return redirect(f"http://{host_ip}:8081/?action=stream")


# Run from the top whopa directory:
#   $ python website_code/app.py
#   * Running on http://0.0.0.0:5000/

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
