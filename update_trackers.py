
import ipaddress
import json
import os
import urllib.request
from urllib.parse import urlsplit

SOURCE_URL = "https://cf.trackerslist.com/best.txt"
OUTPUT_FILE = "rules/trackers.json"

def main():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "sing-box-tracker-updater/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read().decode("utf-8")

    domains = set()
    ip_addresses = set()

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        try:
            parsed = urlsplit(line)

            if not parsed.scheme or not parsed.hostname:
                continue

            host = parsed.hostname.rstrip(".").lower()

            try:
                address = ipaddress.ip_address(host)
                prefix = 32 if address.version == 4 else 128
                ip_addresses.add(f"{address}/{prefix}")
            except ValueError:
                host = host.encode("idna").decode("ascii")
                domains.add(host)

        except (ValueError, UnicodeError):
            continue

    if not domains and not ip_addresses:
        raise RuntimeError("No valid tracker entries found")

    rules = {}

    if domains:
        rules["domain_suffix"] = sorted(domains)

    if ip_addresses:
        rules["ip_cidr"] = sorted(ip_addresses)

    result = {
        "version": 1,
        "rules": [rules]
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Domains: {len(domains)}")
    print(f"IP addresses: {len(ip_addresses)}")
    print(f"Total entries: {len(domains) + len(ip_addresses)}")

if __name__ == "__main__":
    main()
