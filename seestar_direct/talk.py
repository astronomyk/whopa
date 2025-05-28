from time import sleep
from datetime import datetime
from seestar_connect import send_command


def update_time():
    now = datetime.now()
    print(now)
    date_json = {"year": now.year,
                 "mon": now.month,
                 "day": now.day,
                 "hour": now.hour,
                 "min": now.minute,
                 "sec": now.second,
                 "time_zone": "Australia/Melbourne"}
    params = {'method': 'pi_set_time', 'params': [date_json]}
    send_command(params)

    params = {'method': 'pi_get_time'}
    send_command(params)


def set_eq_mode():
    params = {"method": "scope_park", "params": {"equ_mode": True}}
    send_command(params)
    sleep(2)
    params = {"method": "get_device_state"}
    send_command(params)


def move_to_horizon():
    params = {'method': 'scope_move_to_horizon'}
    send_command(params)

    for i in range(10):
        sleep(2)
        params = {'method': 'scope_get_horiz_coord'}
        send_command(params)


def park_scope():
    params = {'method': 'scope_park'}
    send_command(params)


def get_coords():
    # params = {'method': 'scope_get_ra_dec'}

    params = {'method': 'scope_get_equ_coord'}
    send_command(params)

    sleep(2)
    params = {'method': 'scope_get_horiz_coord'}
    send_command(params)


