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
        logger.info(f"User created: {username}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"User already exists: {username}")
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    try:
        logger.debug(f"Auth attempt for {username}")
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        
        if result:
            if result[0] == hash_password(password):
                logger.info(f"Successful login: {username}")
                return True
            logger.warning(f"Invalid password for: {username}")
        else:
            logger.warning(f"Unknown user: {username}")
        return False
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise
    finally:
        conn.close()

def logout_user():
    logger.info(f"User logged out")
    st.session_state.clear()

def get_user_permissions(username):
    conn = sqlite3.connect('users.db')
    try:
        c = conn.cursor()
        c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        return json.loads(result[0]) if result and result[0] else {}
    except Exception as e:
        logger.error(f"Permission fetch failed: {str(e)}")
        return {}
    finally:
        conn.close()

init_db()
