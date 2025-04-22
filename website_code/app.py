import io
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, flash, send_file

from trycoo_code.talk_to_node import send_command
from website_code.plot_wind_from_bom import plot_vic_wind_data_with_quivers
from website_code.plot_object_visibility import plot_altitude_for_seasons  # your updated plotting function
from website_code.astro_utils import get_sun_moon_altitudes

import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages

@app.route("/", methods=["GET", "POST"])
def dashboard():
    celestial = get_sun_moon_altitudes()
    return render_template("dashboard.html", celestial=celestial)


@app.route("/observatory", methods=["GET", "POST"])
def observatory():
    if request.method == "POST":
        if "open_roof" in request.form:
            result = send_command("motor_fwd")
            flash(f"🚪 Roof Opening → {result}")
        elif "close_roof" in request.form:
            result = send_command("motor_rev")
            flash(f"🔒 Roof Closing → {result}")
        elif "stop_roof" in request.form:
            result = send_command("motor_stop")
            flash(f"🛑 Roof Stopped → {result}")
        elif "light_on" in request.form:
            result = send_command("light_on")
            flash(f"💡 Light On → {result}")
        elif "light_off" in request.form:
            result = send_command("light_off")
            flash(f"🌑 Light Off → {result}")
    return render_template("observatory.html")



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
#   * Running on http://127.0.0.1:5000/

if __name__ == "__main__":
    app.run(debug=True)
