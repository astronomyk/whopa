from datetime import datetime
import pytz

import asyncio
import aiohttp

from scipy.interpolate import griddata
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap


async def fetch_json(session, url, station_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return (station_id, data)
    except Exception as e:
        print(f"Error fetching {station_id}: {e}")
        return (station_id, None)


async def fetch_all_jsons(station_ids):
    base_url = "http://www.bom.gov.au/fwo/IDV60801/IDV60801.{station_id}.json"
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_json(session, base_url.format(station_id=station_id), station_id)
            for station_id in station_ids
        ]
        return await asyncio.gather(*tasks)


def get_all_station_data(station_ids):
    try:
        return asyncio.run(fetch_all_jsons(station_ids))
    except RuntimeError:
        # For Jupyter compatibility
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(fetch_all_jsons(station_ids))


def is_inside_map(lon, lat, ax):
    """Returns True if (lon, lat) is within the visible map bounds of the given axis."""
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    return xlim[0] <= lon <= xlim[1] and ylim[0] <= lat <= ylim[1]


def get_delta_time(timestamp_str):
    """Returns the time delta (in hours) between now and the given BoM timestamp."""
    try:
        # Parse string and localize to Melbourne time
        obs_time = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        melb_tz = pytz.timezone("Australia/Melbourne")
        now = datetime.now(melb_tz)
        obs_time = melb_tz.localize(obs_time)

        # Return difference in hours (as float)
        delta = now - obs_time
        return delta.total_seconds() / 3600
    except Exception as e:
        print(f"Timestamp parse error: {e}")
        return None


def wind_dir_to_uv(wind_dir):
    """Convert compass wind direction string to unit vector (u, v)."""
    compass_dirs = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
    }

    angle = compass_dirs.get(wind_dir.upper(), None)
    if angle is None:
        return 0, 0  # Unknown direction

    rad = np.deg2rad(angle)
    u = np.sin(rad)  # x-direction
    v = np.cos(rad)  # y-direction
    return u, v


def wind_speed_color(speed):
    if speed is None:
        return 'gray'
    elif speed < 40:
        return 'green'
    elif speed <= 60:
        return 'orange'
    else:
        return 'red'

def plot_vic_wind_data_with_quivers(return_fig=False):
    center_lat = -37.3031
    center_lon = 144.4165

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axis('equal')
    ax.set_title("Wind Speed & Direction - Victoria")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(center_lon - 0.78, center_lon + 0.78)
    ax.set_ylim(center_lat - 0.78, center_lat + 0.78)
    ax.axhline(center_lat, linestyle='--', color='gray')
    ax.axvline(center_lon, linestyle='--', color='gray')
    ax.autoscale(False)

    # Add a translucent circle around the center (e.g. 0.2° radius)
    center_circle = Circle(
        (center_lon, center_lat),
        radius=0.1,
        edgecolor='none',
        facecolor='grey',
        alpha=0.5,
        zorder=0
    )
    ax.add_patch(center_circle)

    # Collect valid values
    points = []  # (lon, lat)
    values = []  # wind speed
    u_values = []
    v_values = []

    station_ids = [95853, 94852, 94860, 94866, 94856, 94859,
                   94863, 94865, 94849, 95845, 94855, 94874,
                   95840, 94834, 94839, 95836, 94881, 94864,
                   95864, 95833, 94876]

    station_data = get_all_station_data(station_ids)

    for station_id, data in station_data:
        if data is None:
            continue  # Skip if fetch failed

        try:
            obs = data["observations"]["data"][0]
            # (continue as before...)

            obs = data["observations"]["data"][0]
            lat = obs["lat"]
            lon = obs["lon"]

            station_name = obs.get("name", f"Station {station_id}")
            timestamp_str = obs.get("local_date_time_full")
            time_str = obs.get("local_date_time", "N/A")
            delta_hours = get_delta_time(timestamp_str)
            wind_spd = obs.get("wind_spd_kmh", None)
            wind_dir = obs.get("wind_dir", "")

            # Check recency
            if delta_hours is None or delta_hours > 1:
                wind_spd = np.nan

            # Inside your loop, where wind_spd is valid
            if not np.isnan(wind_spd):
                points.append((lon, lat))
                values.append(wind_spd)

                u_raw, v_raw = wind_dir_to_uv(wind_dir)
                u_values.append(u_raw * wind_spd)
                v_values.append(v_raw * wind_spd)

            # Check if point is within bounds
            if is_inside_map(lon, lat, ax):
                # Plot point
                ax.plot(lon, lat, 'ro', alpha=0.3) if np.isnan(
                    wind_spd) else ax.plot(lon, lat, 'bo')

                # Quiver for valid wind
                if not np.isnan(wind_spd):
                    u, v = wind_dir_to_uv(wind_dir)
                    scale_factor = 0.001
                    u *= wind_spd * scale_factor
                    v *= wind_spd * scale_factor
                    color = wind_speed_color(wind_spd)
                    ax.quiver(lon, lat, u, v, color=color, width=0.005)

                    # Annotation
                    label_text = f"{wind_spd} km/h\n{time_str.split('/')[-1]}\n{station_name}"
                else:
                    # Annotation
                    label_text = f"{station_name}"

                ax.text(lon, lat + 0.02, label_text, fontsize=9, va="bottom", ha="center")

        except Exception as e:
            print(f"Failed for station {station_id}: {e}")

    # Create grid
    grid_x, grid_y = np.meshgrid(
        np.linspace(center_lon - 1., center_lon + 1., 200),
        np.linspace(center_lat - 1., center_lat + 1., 200)
    )

    # Interpolate
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
    grid_z = np.clip(grid_z, 0, 100)

    # Interpolate wind components and speed at center
    interp_speed = griddata(points, values, (center_lon, center_lat), method='cubic')
    interp_u = griddata(points, u_values, (center_lon, center_lat), method='cubic')
    interp_v = griddata(points, v_values, (center_lon, center_lat), method='cubic')

    if interp_u is not None and interp_v is not None:
        center_color = wind_speed_color(interp_speed)
        scale_factor = 0.001  # same as other arrows
        ax.quiver(
            center_lon, center_lat,
            interp_u * scale_factor, interp_v * scale_factor,
            color=center_color, width=0.005
        )

        ax.text(
            center_lon,
            center_lat - 0.1,
            f"{interp_speed:.1f} km/h \n WHOPA est.",
            fontsize=11,
            fontweight='bold',
            color='darkred',
            ha='center',
            va='top',
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none')
        )

    # Define colors and corresponding speed thresholds
    color_points = [
        (0.0, '#c7e9b4'),  # 0 km/h → light green
        (0.4, '#7fcdbb'),  # ~40 km/h
        (0.6, '#fecc5c'),  # ~60 km/h
        (0.8, '#f03b20'),  # ~80 km/h
        (1.0, '#bd0026'),  # 100+ km/h
    ]

    # Build a smoothly interpolated custom colormap
    smooth_cmap = LinearSegmentedColormap.from_list("smooth_wind_cmap",
                                                    color_points)

    # Optional: add colormap before other plots so it sits in the background
    cf = ax.contourf(
        grid_x, grid_y, grid_z,
        levels=100,  # many levels for a smooth gradient
        cmap=smooth_cmap,
        vmin=0, vmax=100,  # map 0–100 km/h to the full color range
        alpha=0.6,
        zorder=-1
    )

    # Add bold contour lines every 10 km/h
    # Define contour levels
    contour_levels = np.arange(0, 101, 10)  # Every 10 km/h
    plt.colorbar(cf, ax=ax, label="Interpolated Wind Speed (km/h)",
                 ticks=contour_levels)

    # Draw contour lines
    contour_lines = ax.contour(
        grid_x, grid_y, grid_z,
        levels=contour_levels,
        colors='gray',
        linewidths=0.8,
        linestyles='solid',
        zorder=0
    )

    # Add labels directly onto the contour lines
    ax.clabel(
        contour_lines,
        fmt='%d km/h',  # Format each label
        fontsize=8,
        inline=True,  # Draw on top of line
        inline_spacing=5  # Small spacing tweak
    )

    legend_elements = [
        Line2D([0], [0], color='green', lw=3, label='Wind < 40 km/h'),
        Line2D([0], [0], color='orange', lw=3, label='40–60 km/h'),
        Line2D([0], [0], color='red', lw=3, label='> 60 km/h'),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    plt.grid(True, ls=":")

    if return_fig:
        return fig
    else:
        plt.show()

# plot_vic_wind_data_with_quivers()
