import io
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, flash, send_file

from trycoo_code.talk_to_node import send_command
from website_code.plot_wind_from_bom import plot_vic_wind_data_with_quivers
from website_code.astro_utils import get_sun_moon_altitudes


app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages

@app.route("/", methods=["GET", "POST"])
def index():
    celestial = get_sun_moon_altitudes()

    if request.method == "POST":
        if "open_roof" in request.form:
            result = send_command("motor_fwd")
            flash(f"🚪 Roof Opening → {result}")
        elif "close_roof" in request.form:
            result = send_command("motor_rev")
            flash(f"🔒 Roof Closing → {result}")
    return render_template("index.html", celestial=celestial)


@app.route("/telescope")
def telescope_page():
    # Option 1: embed
    return render_template("telescope.html")
    # Option 2: redirect to port 5432
    # return redirect("http://localhost:5432")


@app.route("/webcam")
def webcam_page():
    return render_template("webcam.html")  # You can update this with your stream


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


if __name__ == "__main__":
    app.run(debug=True)
