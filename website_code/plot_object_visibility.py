import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astroquery.simbad import Simbad
import astropy.units as u
import numpy as np

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u


def get_object_coords(name):
    """Query Simbad to get SkyCoord of a named object."""
    result = Simbad.query_object(name)
    if result is None or len(result) == 0:
        raise ValueError(f"❌ SIMBAD could not find object: '{name}'")

    ra = result["ra"][0]
    dec = result["dec"][0]
    return SkyCoord(str(ra) + " " + str(dec), unit=(u.hourangle, u.deg),
                    frame="icrs")


def plot_altitude_for_seasons(
        object_name,
        min_altitude=30,
        save_path=None
):
    """Plots altitude vs. time for an object over a night for four seasonal dates."""
    location_lat = -37.30303,
    location_lon = 144.41624,
    location_name = "Tylden, VIC"

    location = EarthLocation(lat=location_lat * u.deg, lon=location_lon * u.deg)
    dates = ["2025-03-21", "2025-06-21", "2025-09-21", "2025-12-21"]
    labels = ["March Equinox", "June Solstice", "September Equinox",
              "December Solstice"]
    colors = ["blue", "green", "orange", "red"]

    # Finer granularity: every 10 minutes = 1/6 hour
    hours = np.arange(20, 30, 1 / 6)  # from 20:00 to 05:00

    def times_utc(date):
        utc_offset = location.lon.value / 15  # Convert degrees to hours
        times = [f"{date}T{int(h % 24):02d}:{int((h % 1) * 60):02d}:00" for h in
                 hours]
        return Time(times) - utc_offset * u.hour

    obj_coord = get_object_coords(object_name)

    plt.figure(figsize=(10, 6))

    # Add shaded gray band between 0–30° altitude
    plt.axhspan(0, min_altitude, facecolor='darkgray', alpha=0.4, zorder=0)

    for i, date in enumerate(dates):
        times = times_utc(date)
        altaz_frame = AltAz(obstime=times, location=location)
        altaz = obj_coord.transform_to(altaz_frame)
        altitudes = altaz.alt.deg

        plt.plot(hours, altitudes, label=labels[i], color=colors[i])
        above_mask = np.array(altitudes) >= min_altitude
        plt.fill_between(hours, altitudes, min_altitude,
                         where=above_mask, interpolate=True,
                         color=colors[i], alpha=0.2)

    # Format x-axis ticks
    tick_hours = np.arange(20, 30)
    tick_labels = [str(int(h % 24)) for h in tick_hours]

    plt.title(f"Altitude of {object_name} over {location_name}")
    plt.xlabel("Local Time (Hour)")
    plt.ylabel("Altitude (degrees)")
    plt.xlim(20, 29)
    plt.xticks(tick_hours, tick_labels)

    plt.axhline(min_altitude, color='gray', linestyle='--', linewidth=1,
                label=f"{min_altitude}° Threshold")
    plt.grid(True)
    plt.legend()
    plt.ylim(0, 90)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, format='png')  # Accept BytesIO or file path
        plt.close()
    else:
        plt.show()


# Example usage:
# plot_altitude_for_seasons("ABCdef")
