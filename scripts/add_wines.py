#!/usr/bin/env python3
"""Add wines from a JSON file to a running Wine Cellar instance through its API.

Each entry is a wine object as accepted by POST /wines (name, producer, vintage, type, grape, region,
country, alcohol, quantity, price, barcode, description, notes, pairings, url, profile_fruit,
profile_personality, sweetness ...). The extra key "image_source_url" (https) makes the server fetch
the photo and store it locally. A wine whose name and producer already exist is skipped.

    KELLERLOG_ADMIN_PASSWORD=... python3 scripts/add_wines.py https://wine-cellar.nashome wines.json [--dry-run] [--cafile ca.crt]

Credentials come from the environment (or ./.env for the dev stack), never from the command line.
The NAS certificate is signed by the home LAN CA (see make_lan_cert.sh), which Python does not read from the
macOS keychain: pass that CA's public ca.crt with --cafile or KELLERLOG_CA_FILE.
"""
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env_file():
    p = Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


SSL_CONTEXT = None


def call(method, url, token=None, payload=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as r:
        return json.loads(r.read().decode())


def main():
    global SSL_CONTEXT
    argv = sys.argv[1:]
    cafile = os.environ.get("KELLERLOG_CA_FILE")
    if "--cafile" in argv:
        i = argv.index("--cafile")
        if i + 1 >= len(argv):
            sys.exit("--cafile needs a path")
        cafile = argv[i + 1]
        del argv[i:i + 2]
    if cafile:
        SSL_CONTEXT = ssl.create_default_context(cafile=cafile)
    args = [a for a in argv if not a.startswith("--")]
    dry = "--dry-run" in argv
    if len(args) != 2:
        sys.exit(__doc__)
    base, path = args[0].rstrip("/"), Path(args[1])
    wines = json.loads(path.read_text(encoding="utf-8"))
    load_env_file()
    user, pw = os.environ.get("KELLERLOG_ADMIN_USER", "admin"), os.environ.get("KELLERLOG_ADMIN_PASSWORD")
    if not pw:
        sys.exit("KELLERLOG_ADMIN_PASSWORD is not set")
    token = call("POST", f"{base}/api/auth/login", payload={"username": user, "password": pw})["token"]
    existing = {((w["name"] or "").lower(), (w["producer"] or "").lower()) for w in call("GET", f"{base}/api/export/json", token)}
    created = 0
    for w in wines:
        key = (w["name"].lower(), (w.get("producer") or "").lower())
        if key in existing:
            print(f"skip (already there): {w['name']}")
            continue
        if dry:
            print(f"would add: {w['name']} x{w.get('quantity', 1)}")
            continue
        body = {k: v for k, v in w.items() if k != "image_source_url"}
        if w.get("image_source_url"):
            try:
                body["image_url"] = call("POST", f"{base}/api/upload-from-url", token, {"url": w["image_source_url"]})["url"]
            except urllib.error.HTTPError as e:
                print(f"  photo not imported for {w['name']} ({e.code})")
        res = call("POST", f"{base}/api/wines", token, body)
        created += 1
        print(f"added: {res['name']} x{res['quantity']} (id {res['id']})")
    print(f"done: {created} added")


if __name__ == "__main__":
    main()
