import sys
import socket
import json

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


def parse_params(param_str: str):
    if not param_str:
        return None
    try:
        # Replace curly quotes and convert to proper dict/list syntax
        cleaned = param_str.replace("'", "\"")
        return json.loads(cleaned)
    except json.JSONDecodeError:
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python seestar_direct.py <method_name> [params]")
        sys.exit(1)

    method = sys.argv[1]
    raw_params = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    parsed_params = parse_params(raw_params)

    payload = {"method": method}
    if parsed_params is not None:
        payload["params"] = parsed_params

    print("Constructed payload:")
    print(json.dumps(payload, indent=2))

    # return send_command(payload)


if __name__ == "__main__":
    main()
