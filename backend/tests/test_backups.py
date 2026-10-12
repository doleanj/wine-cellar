import sqlite3
import time
from pathlib import Path

import backups
import main


def test_manual_backup_is_a_valid_database(client, admin_headers):
    client.post("/wines", json={"name": "Backup Wine", "producer": "P"}, headers=admin_headers)
    r = client.post("/backups", headers=admin_headers)
    assert r.status_code == 200
    entry = r.json()
    assert entry["reason"] == "manual" and entry["size"] > 0
    dl = client.get(f"/backups/{entry['name']}", headers=admin_headers)
    assert dl.status_code == 200 and dl.content[:15] == b"SQLite format 3"
    # the copy really contains the data
    path = main.BACKUPS_DIR / entry["name"]
    names = [row[0] for row in sqlite3.connect(path).execute("select name from wine_library")]
    assert "Backup Wine" in names


def test_list_requires_admin_and_is_newest_first(client, admin_headers):
    assert client.get("/backups").status_code == 401
    assert client.post("/backups").status_code == 401
    client.post("/backups", headers=admin_headers)
    time.sleep(1.1)
    client.post("/backups", headers=admin_headers)
    names = [b["name"] for b in client.get("/backups", headers=admin_headers).json()]
    assert names == sorted(names, reverse=True) and len(names) >= 2


def test_download_rejects_path_traversal_and_unknown(client, admin_headers):
    assert client.get("/backups/..%2Fwines.db", headers=admin_headers).status_code == 404
    assert client.get("/backups/wines-20200101-000000-manual.db", headers=admin_headers).status_code == 404
    assert client.get("/backups/passwd", headers=admin_headers).status_code == 404


def test_prune_keeps_newest_per_reason(tmp_path):
    d = tmp_path / "b"
    d.mkdir()
    for i in range(5):
        (d / f"wines-20260101-00000{i}-daily.db").write_bytes(b"x")
    (d / "wines-20250101-000000-startup.db").write_bytes(b"x")
    backups.prune(d, "daily", 2)
    left = sorted(p.name for p in d.iterdir())
    assert left == ["wines-20250101-000000-startup.db", "wines-20260101-000003-daily.db", "wines-20260101-000004-daily.db"]


def test_db_path_from_url():
    assert backups.db_path_from_url("sqlite:////app/data/wines.db") == Path("/app/data/wines.db")
    assert backups.db_path_from_url("sqlite:///rel/x.db") == Path("rel/x.db")
    assert backups.db_path_from_url("postgresql://u@h/db") is None
    assert backups.db_path_from_url("sqlite:///:memory:") is None
