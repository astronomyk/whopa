import subprocess


def is_process_running(process_name):
    """Check if a process is running by name."""
    try:
        result = subprocess.run(["pgrep", "-f", process_name],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def start_script_if_not_running(process_name, script_path):
    """Start the script if the named process is not running."""
    if not is_process_running(process_name):
        subprocess.Popen(["/bin/bash", script_path],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
