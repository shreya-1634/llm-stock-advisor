import sqlite3

DB_FILE = "users.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        email TEXT PRIMARY KEY,
        password TEXT,
        verified BOOLEAN,
        permissions TEXT,
        tokens TEXT
    )
""")

conn.commit()
conn.close()

print("✅ users.db initialized with users table.")
