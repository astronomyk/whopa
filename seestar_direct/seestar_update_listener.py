import requests
import json
from bs4 import BeautifulSoup

status_dict = {}

def parse_html_data(html):
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    for row in soup.select("div.row"):
        cols = row.select("div.col")
        if len(cols) >= 2:
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            try:
                value = float(value) if "." in value else int(value)
            except ValueError:
                pass
            data[key] = value
    return data

def listen_to_status_updates(url):
    print(f"📡 Connecting to {url}...")
    with requests.get(url, stream=True) as resp:
        event_type = None
        data_lines = []

        for line in resp.iter_lines(decode_unicode=True):
            line = line.strip()
            if not line:
                # End of current event block
                if not data_lines:
                    continue
                full_data = "\n".join(data_lines).strip()

                # Process based on event_type
                if event_type == "statusUpdate":
                    for part in data_lines:
                        part = part.strip()
                        if not part:
                            continue
                        try:
                            data = json.loads(part)
                            status_dict.update(data)
                            print("🔄 JSON update:", data)
                        except json.JSONDecodeError:
                            html_info = parse_html_data(part)
                            if html_info:
                                status_dict.update(html_info)
                                print("🧩 HTML update:", html_info)

                elif event_type == "capture_status":
                    try:
                        data = json.loads(full_data)
                        status_dict["capture_status"] = data.get("state", "unknown")
                        print("🎯 Capture status:", data)
                    except json.JSONDecodeError:
                        print(f"⚠️ Invalid JSON for capture_status: {full_data}")

                # Reset after processing
                event_type = None
                data_lines = []

            elif line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()

            elif line.startswith("data:"):
                data_lines.append(line[5:].strip())

            elif not event_type and line.startswith("<div"):
                # orphaned HTML block (still valid, just no event:)
                html_info = parse_html_data(line)
                if html_info:
                    status_dict.update(html_info)
                    print("🧩 HTML update (no event header):", html_info)

if __name__ == "__main__":
    SEESTAR_IP = "100.73.152.103"  # Replace with your Seestar IP
    STATUS_URL = f"http://{SEESTAR_IP}:7556/1/live/status"
    try:
        listen_to_status_updates(STATUS_URL)
    except Exception as e:
        print("💥 Error occurred:", e)
