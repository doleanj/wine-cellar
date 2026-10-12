"""Consistent SQLite backups of the wine database (live-safe, via the sqlite3 backup API).

Files live next to the database (<data>/backups by default) as wines-YYYYMMDD-HHMMSS-<reason>.db.
Reasons: "startup" (taken before migrations when the app starts), "daily" (scheduled), "manual".
Each reason keeps its own newest N files so frequent redeploys never push out the daily ones.
"""
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

REASONS = ("startup", "daily", "manual")
NAME_RE = re.compile(r"^wines-\d{8}-\d{6}-(startup|daily|manual)\.db$")


def db_path_from_url(url: str) -> Optional[Path]:
    """Path of the SQLite file for a SQLAlchemy URL, or None (non-sqlite / in-memory)."""
    m = re.match(r"^sqlite:///(.+)$", url or "")
    if not m or m.group(1) in ("", ":memory:"):
        return None
    return Path(m.group(1))


def backup_db(db_path: Path, backups_dir: Path, reason: str, keep: int) -> Optional[Path]:
    """Copy the live database to backups_dir; prune old files of the same reason. None if there is nothing to copy."""
    if reason not in REASONS:
        raise ValueError("unknown backup reason")
    if not db_path.exists() or db_path.stat().st_size == 0:
        return None
    backups_dir.mkdir(parents=True, exist_ok=True)
    dest = backups_dir / f"wines-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{reason}.db"
    src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    prune(backups_dir, reason, keep)
    return dest


def list_backups(backups_dir: Path) -> List[dict]:
    """Newest first: [{name, reason, size, created (unix seconds)}]."""
    if not backups_dir.exists():
        return []
    out = []
    for p in backups_dir.iterdir():
        m = NAME_RE.match(p.name)
        if m and p.is_file():
            st = p.stat()
            out.append({"name": p.name, "reason": m.group(1), "size": st.st_size, "created": int(st.st_mtime)})
    return sorted(out, key=lambda b: b["name"], reverse=True)


def prune(backups_dir: Path, reason: str, keep: int) -> None:
    same = [b for b in list_backups(backups_dir) if b["reason"] == reason]
    for b in same[max(keep, 1):]:
        (backups_dir / b["name"]).unlink(missing_ok=True)


def newest_age_seconds(backups_dir: Path, reason: Optional[str] = None) -> Optional[float]:
    """Age in seconds of the newest backup (optionally of one reason), None if there is none."""
    items = [b for b in list_backups(backups_dir) if reason is None or b["reason"] == reason]
    return (time.time() - items[0]["created"]) if items else None
