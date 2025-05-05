#!/usr/bin/env python3

from datetime import datetime, timedelta
import subprocess
import os

LOG_PATH = "/home/ingo/WHOPA/actuator_log.txt"
TIMEOUT_SECONDS = 60


def last_actuator_time():
    if not os.path.exists(LOG_PATH):
        return None, None
    with open(LOG_PATH, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return None, None
        last = lines[-1]
        timestamp_str, action = last.rsplit(" ", 1)
        timestamp = datetime.fromisoformat(timestamp_str)
        return timestamp, action


def stop_actuator():
    print("🛑 Timeout reached — sending OFF to actuator")
    subprocess.run([
        "mpremote", "connect", "/dev/ttyACM1",
        "exec", "device='Actuator'; action='off'; exec(open('pico_switches_action.py').read())"
    ])


def main():
    last_time, last_action = last_actuator_time()
    if not last_time or last_action not in ["extend", "retract"]:
        return  # Nothing to stop

    if datetime.now() - last_time > timedelta(seconds=TIMEOUT_SECONDS):
        stop_actuator()


if __name__ == "__main__":
    main()
