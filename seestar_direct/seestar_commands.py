import json
import socket
from datetime import datetime

DEFAULT_IP = "10.42.0.236"
DEFAULT_PORT = 4700


def send_command(params, verbose=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((DEFAULT_IP, DEFAULT_PORT))

    # params = {"method":"scope_park","params":{"equ_mode":self.is_EQ_mode}}
    cmd = {"id": 1}
    cmd.update(params)

    message = json.dumps(cmd) + "\r\n"
    print(f"\nSending: {message.strip()}")
    s.sendall(message.encode())

    # Read until we get a complete message (ends with \r\n)
    response = ""
    while "\r\n" not in response:
        chunk = s.recv(4096).decode("utf-8")
        if not chunk:
            break
        response += chunk

    s.close()

    if verbose:
        try:
            parsed = json.loads(response.split("\r\n")[0])
            method = parsed.get("method")
            result = parsed.get("result")
            code = parsed.get("code")
            error = parsed.get("error")

            print("\n✅ Response:")
            print(f"  method: {method}")
            print(f"  result: {json.dumps(result, indent=2)}")
            print(f"  code  : {code}")
            print(f"  error : {error}")
        except json.JSONDecodeError:
            print("⚠️ Could not parse response as JSON.")
            print("Raw response:\n", response)

    return response


def set_time():
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
    return send_command(params)


def get_time():
    params = {'method': 'pi_get_time'}
    return send_command(params)


def set_eq_mode():
    params = {"method": "scope_park", "params": {"equ_mode": True}}
    return send_command(params)


def get_device_state():
    params = {"method": "get_device_state"}
    return send_command(params)


def move_to_horizon():
    params = {'method': 'scope_move_to_horizon'}
    return send_command(params)


def park_scope():
    params = {'method': 'scope_park'}
    return send_command(params)


def goto(ra, dec):
    """
    ra : decimal hour angle [0, 24]
    dec : decimal declination [-90, 90]
    """
    params = {'method': 'scope_goto', 'params': [ra, dec]}
    return send_command(params)


def goto_target(target_name, ra, dec):
    """
    ra : decimal hour angle [0, 24]
    dec : decimal declination [-90, 90]
    """
    # params = {'method': 'scope_goto', 'params': [ra, dec]}
    params = {'method': 'iscope_start_view', 'params': {'mode': 'star', 'target_ra_dec': [in_ra, in_dec], 'target_name': target_name, 'lp_filter': False}}
    return send_command(params)


def move(ra_dec=()):
    if isinstance(ra_dec, (tuple, list)) and len(ra_dec) == 2:
        return goto(*ra_dec)
    elif isinstance(ra_dec, str):
        if ra_dec.lower() == "park":
            return park_scope()
        elif ra_dec.lower() == "horizon":
            return move_to_horizon()
    else:
        raise ValueError(
            f"ra_dec must be one of: [(ra, dec), 'park', 'horizon']: {ra_dec}")


def get_coords():
    # params = {'method': 'scope_get_equ_coord'}
    params = {'method': 'scope_get_ra_dec'}
    eq_dict = send_command(params)
    params = {'method': 'scope_get_horiz_coord'}
    altaz_dict = send_command(params)

    return {"ra": eq_dict[0], "dec": eq_dict[1],
            "alt": altaz_dict[0], "az": altaz_dict[1]}


def get_track_state():
    params = {'method': 'scope_get_track_state'}
    return send_command(params)


def set_track_state(flag):
    params = {'method': 'scope_set_track_state', "params": flag}
    return send_command(params)


def track_state(flag=None):
    if flag is None:
        return get_track_state()
    elif isinstance(flag, bool):
        return set_track_state(flag)
    else:
        raise ValueError(f"flag must be one of: [None, True, False]: {flag}")


def set_exposure(exptime, which="stack_l"):
    """which : [stack_l, continuous]"""
    params = {"method": "set_setting", "params": {"exp_ms": {which: exptime}}}
    return send_command(params)


def get_exposure():
    params = {"method": "get_setting"}
    json_dict = send_command(params)
    return json_dict.get("exp_ms")


def exposure(exptime=None, stack_l=True):
    if exptime is None:
        return get_exposure()
    elif isinstance(exptime, int) and isinstance(stack_l, bool):
        return set_exposure(exptime, stack_l)
    else:
        raise ValueError(f"exptime must be one of [None, int]: {exptime}, and stack_l must be boolean: {stack_l}")


def create_dark():
    params = {"method": "start_create_dark"}
    return send_command(params)


def set_filter(pos):
    """
    0: Dark = Shutter closed
    1: Open = 400-700nm, with Bayer RGB matrix
    2: Narrow = 30 nm OIII (Blue) + 20 nm Hα (Red) (also LP: Light Pollution)
    """
    params = {"method": "set_wheel_position", "params": [pos]}
    return send_command(params)


def get_filter():
    params = {"method": "get_wheel_position"}
    return send_command(params)


def filter_wheel(pos=None):
    if pos is None:
        return get_filter()
    elif isinstance(pos, int):
        return set_filter(pos)
    elif isinstance(pos, str) and pos.lower() in ["open", "narrow"]:
        pos_i = {"open": 1, "narrow": 2, "lp": 2}[pos]
        return set_filter(pos)


def set_target_name(name):
    params = {"method": "set_sequence_setting", "params": [{"group_name": name}]}
    return send_command(params)


def get_target_name(name):
    params = {"method": "get_sequence_setting"}
    return send_command(params).get("group_name")
