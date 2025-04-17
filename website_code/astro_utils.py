from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon, SkyCoord
from astropy.coordinates import solar_system_ephemeris
from astropy import units as u
from astroplan import Observer, FixedTarget
from datetime import datetime
import pytz
import numpy as np


def get_sun_moon_altitudes():
    # === 1. Setup ===
    melb = pytz.timezone("Australia/Melbourne")
    now_local = datetime.now(melb)
    now_utc = now_local.astimezone(pytz.utc)
    observing_time = Time(now_utc)

    location = EarthLocation(lat=-37.3031*u.deg, lon=144.4165*u.deg, height=300*u.m)
    observer = Observer(location=location, timezone=melb)

    # === 2. Altitudes ===
    altaz_frame = AltAz(obstime=observing_time, location=location)
    with solar_system_ephemeris.set('builtin'):
        sun = get_sun(observing_time)
        moon = get_moon(observing_time)

        sun_alt = sun.transform_to(altaz_frame).alt
        moon_alt = moon.transform_to(altaz_frame).alt

    # === 3. Moon phase as % ===
    elongation = sun.separation(moon)
    phase_angle = elongation.deg
    illumination = (1 + np.cos(np.deg2rad(phase_angle))) / 2
    moon_illum_percent = round(illumination * 100, 1)

    # === 4. Rise/Set Times ===
    sun_rise = observer.sun_rise_time(observing_time, which='next').to_datetime(timezone=melb)
    sun_set  = observer.sun_set_time(observing_time, which='next').to_datetime(timezone=melb)
    moon_rise = observer.moon_rise_time(observing_time, which='next').to_datetime(timezone=melb)
    moon_set  = observer.moon_set_time(observing_time, which='next').to_datetime(timezone=melb)

    # === 5. Split local time into separate parts ===
    local_date = now_local.strftime("%Y-%m-%d")
    local_time = now_local.strftime("%H:%M")
    timezone = now_local.strftime("%Z")

    # 6=== RA/Dec of Zenith, East, and West Horizon ===
    altaz_frame = AltAz(obstime=observing_time, location=location)

    zenith_altaz = SkyCoord(alt=90 * u.deg, az=0 * u.deg, frame=altaz_frame)
    east_altaz = SkyCoord(alt=0 * u.deg, az=90 * u.deg, frame=altaz_frame)
    west_altaz = SkyCoord(alt=0 * u.deg, az=270 * u.deg, frame=altaz_frame)

    zenith_radec = zenith_altaz.transform_to('icrs')
    east_radec = east_altaz.transform_to('icrs')
    west_radec = west_altaz.transform_to('icrs')

    zenith_dec = int(location.lat.to_value(u.deg))

    # 6=== Current Alt/Az of LMC, Sgr A*, Orion ===
    lmc_alt, lmc_az, lmc_status, lmc_next_rise = altaz_for_object("Large Magellanic Cloud", location, observing_time)
    m42_alt, m42_az, m42_status, m42_next_rise = altaz_for_object("M42", location, observing_time)
    sgrA_alt, sgrA_az, sgrA_status, sgrA_next_rise = altaz_for_object("Sgr A*", location, observing_time)

    return {
        "local_date": local_date,
        "local_time": local_time,
        "timezone": timezone,
        "sun_alt": sun_alt.to_value(u.deg),
        "moon_alt": moon_alt.to_value(u.deg),
        "moon_illum": moon_illum_percent,
        "sun_rise": sun_rise.strftime("%H:%M"),
        "sun_set": sun_set.strftime("%H:%M"),
        "moon_rise": moon_rise.strftime("%H:%M"),
        "moon_set": moon_set.strftime("%H:%M"),
        "moon_illum": moon_illum_percent,
        "moon_emoji": moon_emoji_from_illum(moon_illum_percent),
        "zenith_dec": zenith_dec,
        "zenith_ra": int(zenith_radec.ra.to(u.deg).value),
        "east_ra": int(east_radec.ra.to(u.deg).value),
        "west_ra": int(west_radec.ra.to(u.deg).value),
        "lmc_alt": lmc_alt,
        "lmc_az": lmc_az,
        "lmc_status": lmc_status,
        "lmc_next_rise": lmc_next_rise,
        "m42_alt": m42_alt,
        "m42_az": m42_az,
        "m42_status": m42_status,
        "m42_next_rise": m42_next_rise,
        "sgrA_alt": sgrA_alt,
        "sgrA_az": sgrA_az,
        "sgrA_status": sgrA_status,
        "sgrA_next_rise": sgrA_next_rise,
    }


def altaz_for_object(name, location, observing_time):
    try:
        obj = SkyCoord.from_name(name)
        altaz = obj.transform_to(AltAz(obstime=observing_time, location=location))
        alt = round(altaz.alt.to_value(u.deg), 1)
        az = round(altaz.az.to_value(u.deg), 1)

        # Use astroplan to calculate next rise above 30°
        observer = Observer(location=location, timezone="Australia/Melbourne")
        target = FixedTarget(name=name, coord=obj)
        next_rise = observer.target_rise_time(observing_time, target,
                                              horizon=30*u.deg,
                                              which='next').to_datetime(
                                                  timezone=pytz.timezone("Australia/Melbourne")
                                              )
        next_rise_str = next_rise.strftime("%H:%M")
    except Exception as e:
        alt, az, next_rise_str = None, None, "N/A"

    if alt is None:
        status = "⚠️ Unknown"
    elif alt < 30:
        status = "🔻 Not visible (below 30°)"
    elif az < 180:
        status = "⬆️ Rising"
    else:
        status = "⬇️ Setting"

    return alt, az, status, next_rise_str


def moon_emoji_from_illum(illum):
    # Rough mapping based on illumination %
    if illum < 1:
        return "🌑"  # New Moon
    elif illum < 25:
        return "🌒"  # Waxing Crescent
    elif illum < 50:
        return "🌓"  # First Quarter
    elif illum < 75:
        return "🌔"  # Waxing Gibbous
    elif illum < 100:
        return "🌕"  # Full Moon
    else:
        return "🌕"  # Just in case
