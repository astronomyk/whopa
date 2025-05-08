from sys import argv
import paramiko

HOST = "10.42.0.143"
USER = "ingo"
PASSWD = "monkey"


def run_remote_capture(pi_host=HOST, pi_user=USER, pi_password=PASSWD,
                       exposure=1.0, gain=1.0, add_timestamp=False, stub=None):

    command = f"python3 ~/whopa/raspi_code/allsky_get_image.py {exposure} {gain}"
    if stub is not None:
        command += f" {stub}"
    if add_timestamp:
        command += " --add-timestamp"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(pi_host, username=pi_user, password=pi_password)

    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    errors = stderr.read().decode()

    ssh.close()

    print("=== STDOUT ===")
    print(output)
    if errors:
        print("=== STDERR ===")
        print(errors)


if __name__ == "__main__":
    exposure = float(argv[1]) if len(argv) == 2 else 1
    gain = float(argv[2]) if len(argv) == 3 else 1
    add_timestamp = bool(argv[3]) if len(argv) == 4 else False

    run_remote_capture(exposure=exposure, gain=gain, add_timestamp=add_timestamp)
