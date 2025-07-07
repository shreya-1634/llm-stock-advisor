import sqlite3
import hashlib
import streamlit as st
from datetime import datetime
import json

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password TEXT,
                  permissions TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                 (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == hash_password(password)

def logout_user():
    st.session_state.clear()

def get_user_permissions(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result and result[0] else {}

# Initialize database on import
init_db()
