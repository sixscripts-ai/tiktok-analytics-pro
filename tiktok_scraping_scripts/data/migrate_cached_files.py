#!/usr/bin/env python3
"""One-time script to migrate cached JSON files into the SQLite database."""

import json
from pathlib import Path
from typing import Optional

from storage import Storage


def migrate(data_dir: str = "scraped_data", db_path: Optional[str] = None) -> None:
    dir_path = Path(data_dir)
    dir_path.mkdir(exist_ok=True)
    db_file = Path(db_path) if db_path else dir_path / "cache.db"
    storage = Storage(str(db_file))

    for file in dir_path.glob("*_profile.json"):
        username = file.stem.replace("_profile", "")
        try:
            data = json.loads(file.read_text())
            storage.set_profile(username, data)
        except Exception:
            pass

    for file in dir_path.glob("*_videos.json"):
        username = file.stem.replace("_videos", "")
        try:
            data = json.loads(file.read_text())
            storage.set_videos(username, data)
        except Exception:
            pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate cached JSON files to SQLite database")
    parser.add_argument("--data-dir", default="scraped_data", help="Directory containing cached JSON files")
    parser.add_argument("--db-path", default=None, help="Path to SQLite database file")
    args = parser.parse_args()
    migrate(args.data_dir, args.db_path)
    print("Migration complete")
