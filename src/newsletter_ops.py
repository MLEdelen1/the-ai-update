
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/a0/usr/projects/x-manage/data/db/newsletter.db")

def audit_growth():
    print("[BUSINESS] Auditing Newsletter Growth...")
    if not DB_PATH.exists():
        return "No DB found."

    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    new_today = conn.execute("SELECT COUNT(*) FROM subscribers WHERE created_at > date('now')").fetchone()[0]
    conn.close()

    report = f"Total Subscribers: {count} | New Today: {new_today}"
    print(f"[BUSINESS] {report}")
    return report

if __name__ == '__main__':
    audit_growth()
