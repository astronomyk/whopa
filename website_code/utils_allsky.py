from sys import argv
import paramiko
import re
from pathlib import Path


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

    print(f"Sending command: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    errors = stderr.read().decode()

    ssh.close()

    print("=== STDOUT ===")
    print(output)

    if errors:
        print("=== STDERR ===")
        print(errors)

    # --- Fetch files if filenames found ---
    fits_match = re.search(r"Saved FITS to (.+\.fits)", output)
    jpg_match = re.search(r"Saved JPEG to (.+\.jpg)", output)

    if fits_match and jpg_match:
        remote_fits = fits_match.group(1).strip()
        remote_jpg = jpg_match.group(1).strip()

        local_dir = Path("fetched_images")
        local_dir.mkdir(exist_ok=True)

        local_fits = local_dir / Path(remote_fits).name
        local_jpg = local_dir / Path(remote_jpg).name

        transport = paramiko.Transport((pi_host, 22))
        transport.connect(username=pi_user, password=pi_password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        print(f"Downloading: {remote_fits} → {local_fits}")
        sftp.get(remote_fits, str(local_fits))

        print(f"Downloading: {remote_jpg} → {local_jpg}")
        sftp.get(remote_jpg, str(local_jpg))

        sftp.close()
        transport.close()

        print("✅ Download complete.")
    else:
        print("⚠️ Could not find file paths in output. Nothing downloaded.")


if __name__ == "__main__":
    exposure = float(argv[1]) if len(argv) == 2 else 1
    gain = float(argv[2]) if len(argv) == 3 else 1
    add_timestamp = bool(argv[3]) if len(argv) == 4 else False

    run_remote_capture(exposure=exposure, gain=gain, add_timestamp=add_timestamp)
