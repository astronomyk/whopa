import sys
import json


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
