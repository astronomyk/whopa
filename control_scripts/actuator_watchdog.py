#!/usr/bin/env python3

from datetime import datetime, timedelta
import subprocess
import os

LOG_PATH = "/home/ingo/WHOPA/actuator_log.txt"
TIMEOUT_SECONDS = 30


def read_last_line(filepath):
    with open(filepath, 'rb') as f:
        try:
            f.seek(-2, 2)
            while f.read(1) != b'\n':
                f.seek(-2, 1)
        except OSError:
            f.seek(0)
        return f.readline().decode().strip()


def last_actuator_time():
    if not os.path.exists(LOG_PATH):
        return None, None
    last = read_last_line(LOG_PATH)
    timestamp_str, action = last.rsplit(" ", 1)
    timestamp = datetime.fromisoformat(timestamp_str)
    return timestamp, action


def stop_actuator():
    print("🛑 Timeout reached — sending OFF to actuator")
    subprocess.run([
        "/home/ingo/.pyenv/shims/mpremote", "connect", "/dev/ttyACM1",
        "exec", "device='Actuator'; action='off'; exec(open('pico_switches_action.py').read())"
    ])
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.now().isoformat()} off\n")


def main():
    last_time, last_action = last_actuator_time()
    if not last_time or last_action not in ["extend", "retract"]:
        return  # Nothing to stop

    if datetime.now() - last_time > timedelta(seconds=TIMEOUT_SECONDS):
        stop_actuator()


if __name__ == "__main__":
    main()
