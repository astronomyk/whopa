import sys
import socket
import json

DEFAULT_IP = "10.42.0.236"
DEFAULT_PORT = 4700


def send_command(ip, command):
    port = DEFAULT_PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    cmd = {"id": 1, "method": command}
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


def main():
    ip = DEFAULT_IP

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python seestar_get_cli.py <get_command>")
        sys.exit(1)

    arg = sys.argv[1]

    # Send the selected command without checking a predefined list
    send_command(ip, arg)


if __name__ == "__main__":
    main()
