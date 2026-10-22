import sqlite3
from pathlib import Path

db_path = Path("data/applications.db")

print("Database exists:", db_path.exists())

if db_path.exists():
    print("Database size:", db_path.stat().st_size, "bytes")

    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "PRAGMA integrity_check;"
        ).fetchall()

        print("Integrity check:", result)