from datetime import datetime
from seestar_connect import send_command

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

# Send the selected command without checking a predefined list
# send_command(params)

params = {'method': 'pi_get_time'}
send_command(params)
