from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
from astropy import units as u


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


from pyongc import data
NGC_CAT = data.all()


def find_ngc_near_zenith(latitude=-37.303071, longitude=144.41625, elevation=550, radius_deg=30):
    location = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=elevation*u.m)
    now = Time(datetime.utcnow())
    altaz_frame = AltAz(obstime=now, location=location)
    zenith = SkyCoord(alt=90*u.deg, az=0*u.deg, frame=altaz_frame).transform_to('icrs')

    catalog = NGC_CAT.dropna(subset=['ra', 'dec', 'majax', 'minax'])

    coords = SkyCoord(ra=catalog['ra'].values*u.rad, dec=catalog['dec'].values*u.rad)
    separations = zenith.separation(coords)
    mask = separations < radius_deg * u.deg
    near_zenith = catalog[mask].copy()

    # Transform to AltAz for azimuth
    altaz = coords[mask].transform_to(altaz_frame)
    near_zenith['separation_deg'] = separations[mask].deg
    near_zenith['azimuth_deg'] = altaz.az.deg
    near_zenith['sky_area'] = near_zenith['majax'] * near_zenith['minax']

    return near_zenith[['name', 'type', 'ra', 'dec', 'vmag',
                        'majax', 'minax', 'sky_area',
                        'separation_deg', 'azimuth_deg']]


def plot_ngc_polar(catalog_df, label_top_n=5):
    if catalog_df.empty:
        print("No objects to plot.")
        return

    # Convert angles to polar coordinates
    r = catalog_df['separation_deg'].values
    theta = np.radians(catalog_df['azimuth_deg'].values)

    # Color by magnitude
    mag = catalog_df['vmag'].fillna(catalog_df['vmag'].max() + 2)
    colors = plt.cm.plasma((mag - mag.min()) / (mag.max() - mag.min()))

    # Size by log of sky area (avoid log(0) by adding a small value)
    sky_area = catalog_df['sky_area'].values
    safe_area = np.clip(sky_area, a_min=1e-2, a_max=None)  # Avoid zeros
    size = 20 + 30 * np.log10(safe_area)  # Adjust scale and offset as needed

    # Plotting
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
    sc = ax.scatter(theta, r, c=colors, s=size, edgecolors='black', linewidths=0.5)

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, max(r) * 1.05)
    ax.set_title("NGC/IC Objects Near Zenith", fontsize=14)

    # Label N brightest objects
    if label_top_n > 0:
        top_objects = catalog_df.nlargest(label_top_n, 'sky_area')
        for _, row in top_objects.iterrows():
            r_ = row['separation_deg']
            theta_ = np.radians(row['azimuth_deg'])
            ax.text(theta_, r_ + 1, row['name'], ha='center', va='bottom', fontsize=8)

    # Colorbar
    norm = plt.Normalize(vmin=mag.min(), vmax=mag.max())
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap='plasma_r', norm=norm), ax=ax, orientation='vertical')
    cbar.set_label('Magnitude (brighter = bluer)', rotation=270, labelpad=15)

    plt.show()



# results = find_ngc_near_zenith(-37.303071, 144.41625, radius_deg=30)
# plot_ngc_polar(results, label_top_n=30)

