# create_user_db.py
import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        verified BOOLEAN DEFAULT 0,
        permissions TEXT,
        tokens TEXT
    )
""")

conn.commit()
conn.close()

print("✅ users.db created or already exists with updated schema.")
