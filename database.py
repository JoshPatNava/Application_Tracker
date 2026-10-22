# Imports that you are going to be using
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "applications.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_table(): 
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            date_applied DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            job_url TEXT
            notes TEXT
            )
        """)

def add_application(company, position, date_applied, status, job_url, notes):
    with get_connection as conn:
        conn.execute("""
            INSERT INTO applications
                (company, position, date_applied,
                status, job_url, notes)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (company, position, date_applied,
               status, job_url, notes))

def get_application():
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT *
            FROM applications
            ORDER BY date_applied DESC, id DESC
        """)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row))
                for row in cursor.fetchall()]

def check_columns():
    with get_connection() as conn:
        cursor = conn.execute(
            "PRAGMA table_info(applications)"
        )

        for column in cursor.fetchall():
            print(column)