import sqlite3
import hashlib
import json
from datetime import datetime
from core.config import get_logger

logger = get_logger(__name__)

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
    logger.info("Database initialized")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                 (username, hash_password(password)))
        conn.commit()
        logger.info(f"User {username} created")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"User {username} already exists")
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if result and result[0] == hash_password(password):
            logger.info(f"User {username} authenticated")
            return True
        logger.warning(f"Authentication failed for {username}")
        return False
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        return False
    finally:
        conn.close()

def logout_user():
    logger.info(f"User {st.session_state.get('username')} logged out")
    st.session_state.clear()

init_db()

# auth/auth.py
from core.config import get_logger

logger = get_logger(__name__)

# Simple user database (for demo purposes only)
USERS = {
    "admin": {
        "password": "admin123",
        "permissions": ["view", "trade", "admin"]
    },
    "trader": {
        "password": "trader123",
        "permissions": ["view", "trade"]
    },
    "viewer": {
        "password": "viewer123",
        "permissions": ["view"]
    }
}

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user with test credentials"""
    try:
        if username in USERS and USERS[username]["password"] == password:
            logger.info(f"User {username} authenticated successfully")
            return True
        logger.warning(f"Failed login attempt for {username}")
        return False
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False

def logout_user():
    """Logout the current user"""
    logger.info("User logged out")

def check_permission(username: str, permission: str) -> bool:
    """Check if user has specific permission"""
    try:
        return permission in USERS.get(username, {}).get("permissions", [])
    except Exception as e:
        logger.error(f"Permission check error: {str(e)}")
        return False
