#!/usr/bin/env python3
"""Standalone SQLite backup CLI with N-day retention.

Self-contained: stdlib only, no third-party deps, no project coupling. Safe for cron.

Uses SQLite's online backup API, so it works on a live database under concurrent
writes / WAL -- never copy a database file that may be in use.

Example : cron (daily at 03:00, keep 30 days):
    0 3 * * * /path/to/backup-sqlite.py /path/to/db --backup-dir /backups --retention-days 30 --no-compress >> /var/log/sqlite-backup.log 2>&1

To write to /var/log without root, pre-create the file using :
    sudo install -o <user> -g <user> -m 644 /dev/null /var/log/sqlite-backup.log
"""

from __future__ import annotations

import argparse
import gzip
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path


def online_backup(src: Path, dest: Path) -> None:
    """Consistent backup of a live database via the sqlite3 online backup API."""
    with sqlite3.connect(src) as source, sqlite3.connect(dest) as target:
        source.backup(target)


def compress(path: Path) -> Path:
    """Gzip a file in place, removing the original. Returns the .gz path."""
    gz_path = path.with_suffix(path.suffix + ".gz")
    with path.open("rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    path.unlink()
    return gz_path


def prune(
    backup_dir: Path, prefix: str, suffix: str, retention_days: int
) -> list[Path]:
    """Delete backups older than retention_days. Returns the removed paths."""
    cutoff = time.time() - retention_days * 86_400
    removed: list[Path] = []
    for old in backup_dir.glob(f"{prefix}-*{suffix}"):
        if old.is_file() and old.stat().st_mtime < cutoff:
            old.unlink()
            removed.append(old)
    return removed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Online backup of a SQLite database with N-day retention.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("database", type=Path, help="path to the SQLite database")
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="directory for backups (default: <db dir>/backups)",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=30,
        help="delete backups older than this many days",
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="keep the plain .db backup instead of gzipping it",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    db: Path = args.database
    if not db.is_file():
        print(f"error: database not found: {db}", file=sys.stderr)
        return 1

    backup_dir: Path = args.backup_dir or db.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    prefix = db.stem
    suffix = ".db" if args.no_compress else ".db.gz"
    dest = backup_dir / f"{prefix}-{datetime.now():%Y%m%d-%H%M%S}.db"

    online_backup(db, dest)
    if not args.no_compress:
        dest = compress(dest)

    print(f"backup written: {dest}")

    removed = prune(backup_dir, prefix, suffix, args.retention_days)
    if removed:
        print(f"pruned {len(removed)} backup(s) older than {args.retention_days}d")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
