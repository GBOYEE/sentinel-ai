"""Database migration script."""

import os
from sentinel_ai.config import DATABASE_URL
import psycopg2

def init_db():
    if DATABASE_URL.startswith("postgresql"):
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id SERIAL PRIMARY KEY,
                repo TEXT NOT NULL,
                pull_number INTEGER NOT NULL,
                filename TEXT,
                line INTEGER,
                severity TEXT,
                category TEXT,
                description TEXT,
                suggestion TEXT,
                tool TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized")
    else:
        print("SQLite backend not implemented yet; skipping DB setup")

if __name__ == "__main__":
    init_db()
