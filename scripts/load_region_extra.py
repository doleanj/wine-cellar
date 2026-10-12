#!/usr/bin/env python3
"""Upload the longer region texts (made by fetch_leclerc_region_texts.py) to a running Wine Cellar.

    KELLERLOG_ADMIN_USER=admin KELLERLOG_ADMIN_PASSWORD=... \\
        python3 scripts/load_region_extra.py https://wine-cellar.nashome ../wine-cellar-assets/leclerc-regions

Reads <folder>/regions_extra.json and sets each region's `extra` text and `extra_source` link. Regions that are
not in the file keep what they have; the existing intro text and map are never touched. The password is
read from the environment (or ./.env), never from the command line. For a self-signed certificate set
SSL_CERT_FILE to the CA file, or use plain http://.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path


def load_env_file():
    p = Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def call(method, url, token=None, body=None):
    headers = {"Content-Type": "application/json"} if body is not None else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base, folder = sys.argv[1].rstrip("/"), Path(sys.argv[2])
    load_env_file()
    user, pw = os.environ.get("KELLERLOG_ADMIN_USER", "admin"), os.environ.get("KELLERLOG_ADMIN_PASSWORD")
    if not pw:
        sys.exit("KELLERLOG_ADMIN_PASSWORD is not set")
    data = json.loads((folder / "regions_extra.json").read_text(encoding="utf-8"))
    token = call("POST", f"{base}/api/auth/login", body=json.dumps({"username": user, "password": pw}).encode())["token"]
    for region in call("GET", f"{base}/api/regions", token):
        entry = data.get(region["key"])
        if not entry:
            print(f"skipped {region['key']}: no text in the file")
            continue
        update = {"extra": entry["text"], "extra_source": entry.get("source_url", "")}
        call("PUT", f"{base}/api/regions/{region['key']}", token, json.dumps(update).encode())
        print(f"updated {region['key']}: {len(entry['text'])} characters")


if __name__ == "__main__":
    main()
