import io
import base64
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, flash, send_file

from plot_wind_from_bom import plot_vic_wind_data_with_quivers
from plot_object_visibility import plot_altitude_for_seasons  # your updated plotting function
from astro_utils import get_sun_moon_altitudes
# from get_pico_states_mock import load_gpios_yaml, get_mock_sensor_data, get_mock_gpio_states, get_roof_state, get_linux_temperatures  # (we simulate this)
from get_pico_states import load_gpios_yaml, get_sensor_data, get_gpio_states, get_roof_state, get_linux_temperatures


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

    # sensor_data = get_mock_sensor_data()
    # gpio_states = get_mock_gpio_states()
    # roof_state = get_roof_state(sensor_data, gpio_states)
    # linux_temperatures = get_linux_temperatures()

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

    if request.method == "POST":
        action = request.form.get("action")
        flash(f"Command sent: {action}")
        # Here you'd normally send a serial command
        # e.g., serial_write(action)

    return render_template("observatory.html",
                           gpios=gpios_config,
                           sensors=sensor_data,
                           gpio_states=gpio_states,
                           roof_state=roof_state,
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



# Run from the top whopa directory:
#   $ python website_code/app.py
#   * Running on http://0.0.0.0:5000/

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
