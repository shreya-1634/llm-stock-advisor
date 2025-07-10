# create_user_db.py

import sqlite3

def create_user_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Create the users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            permissions TEXT DEFAULT '{}'
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ users.db and users table created successfully.")

if __name__ == "__main__":
    create_user_db()
