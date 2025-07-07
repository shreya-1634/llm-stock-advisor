import sqlite3
import hashlib
import streamlit as st
from datetime import datetime, timedelta
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

def add_user(username, password):
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
    
    if result and result[0] == hash_password(password):
        return True
    return False

def logout_user():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.trading_engine = None

def get_user_permissions(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result and result[0] else {}

def update_user_permissions(username, permissions):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET permissions = ? WHERE username = ?',
              (json.dumps(permissions), username))
    conn.commit()
    conn.close()
