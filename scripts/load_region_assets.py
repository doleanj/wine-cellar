#!/usr/bin/env python3
"""Upload region intro texts and map images to a running Wine Cellar instance.

The assets stay outside the repository (third-party material, personal use):

    assets/regions.json     {"<region key>": "intro text", ...}
    assets/<region key>.png (or .jpg/.webp)

Usage:
    KELLERLOG_ADMIN_USER=admin KELLERLOG_ADMIN_PASSWORD=... \\
        python3 scripts/load_region_assets.py http://localhost:8080 ../wine-cellar-assets/regions

Credentials are read from the environment (or ./.env for the dev stack), never from the command line.
"""
import json
import mimetypes
import os
import sys
import urllib.request
import uuid
from pathlib import Path


def load_env_file():
    p = Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def call(method, url, token=None, body=None, headers=None):
    h = dict(headers or {})
    if token:
        h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def upload_image(base, token, path: Path) -> str:
    boundary = uuid.uuid4().hex
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    res = call("POST", f"{base}/api/upload", token, body, {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return res["url"]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base, folder = sys.argv[1].rstrip("/"), Path(sys.argv[2])
    load_env_file()
    user, pw = os.environ.get("KELLERLOG_ADMIN_USER", "admin"), os.environ.get("KELLERLOG_ADMIN_PASSWORD")
    if not pw:
        sys.exit("KELLERLOG_ADMIN_PASSWORD is not set")
    token = call("POST", f"{base}/api/auth/login", body=json.dumps({"username": user, "password": pw}).encode(),
                 headers={"Content-Type": "application/json"})["token"]
    intros = json.loads((folder / "regions.json").read_text(encoding="utf-8"))
    regions = call("GET", f"{base}/api/regions", token)
    for r in regions:
        key, update = r["key"], {}
        if key in intros:
            update["intro"] = intros[key]
        img = next((p for ext in (".png", ".jpg", ".jpeg", ".webp") if (p := folder / f"{key}{ext}").exists()), None)
        if img:
            update["image_url"] = upload_image(base, token, img)
        if update:
            call("PUT", f"{base}/api/regions/{key}", token, json.dumps(update).encode(), {"Content-Type": "application/json"})
            print(f"updated {key}: {', '.join(update)}")
        else:
            print(f"skipped {key}: nothing to load")


if __name__ == "__main__":
    main()
