from time import sleep
from datetime import datetime
from seestar_direct.seestar_commands import send_command

params = {'method': 'scope_move_to_horizon'}
# params = {'method': 'scope_park'}
# params = {'method': 'get_device_state'}
# params = {'method': 'scope_goto', 'params': [5.63, -69.4]}
# params = {'method': 'scope_goto', 'params': [18.082, -24.3]}
# params = {'method': 'scope_goto', 'params': [0.398, -72]}
# params = {"method": "pi_get_time"}
# params = {'method': 'scope_get_ra_dec'}
# params = {'method': 'scope_set_track_state', "params": False}
# params = {"method": "get_setting"}
# params = {"method": "set_setting", "params": {"exp_ms": {"stack_l": 5000}}}
# params = {"method": "get_wheel_position"}
# params = {"method": "set_wheel_position", "params": [1]}
# params = {"method": "start_create_dark"}
# params = {"method": "set_sequence_setting", "params": [{"group_name": "HelloWorld"}]}
# params = {'method': 'get_sequence_setting'}
# params = {'method': 'get_focuser_position'}
send_command(params)

# for i in range(0):
#     sleep(2)
#     params = {'method': 'scope_get_horiz_coord'}
#     send_command(params)
#     sleep(0.5)
#     params = {'method': 'scope_get_equ_coord'}
#     send_command(params)