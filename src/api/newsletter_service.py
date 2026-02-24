#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/a0/usr/projects/x-manage/data/db/newsletter.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    email TEXT UNIQUE, 
                    source TEXT, 
                    status TEXT, 
                    created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_subscriber(email, source="website"):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO subscribers (email, source, status, created_at) VALUES (?, ?, ?, ?)",
                     (email, source, "active", datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_subscriber_count():
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    conn.close()
    return count

if __name__ == "__main__":
    init_db()
    print(f"Newsletter DB Initialized. Current subs: {get_subscriber_count()}")
