import io
import os
import base64
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, send_from_directory, abort

from plot_wind_from_bom import plot_vic_wind_data_with_quivers
from plot_object_visibility import plot_altitude_for_seasons
from astro_utils import get_sun_moon_altitudes
# from get_mock_states import get_sensor_data, get_gpio_states # (we simulate this)
from get_pico_states import get_sensor_data, get_gpio_states, get_roof_state, get_linux_temperatures, load_gpios_yaml
from utils_picos import set_switch_device_action, compute_tilt_angle

ARCHIVE_PATH = "/media/ingo/archive"


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
def list_files():
    folder_tree = {}

    for root, dirs, files in os.walk(ARCHIVE_PATH):
        rel_root = os.path.relpath(root, ARCHIVE_PATH)
        file_paths = sorted(files)
        if file_paths:
            folder_tree[rel_root] = file_paths

    return render_template("file_tree.html", folder_tree=folder_tree)

@app.route("/download/<path:filename>")
def download_file(filename):
    full_path = os.path.join(ARCHIVE_PATH, filename)

    if not os.path.isfile(full_path):
        abort(404)

    dir_path = os.path.dirname(filename)
    base_name = os.path.basename(filename)
    return send_from_directory(os.path.join(ARCHIVE_PATH, dir_path), base_name, as_attachment=True)


# Run from the top whopa directory:
#   $ python website_code/app.py
#   * Running on http://0.0.0.0:5000/

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
