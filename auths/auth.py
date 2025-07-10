import sqlite3
import bcrypt
from core.config import get_logger

logger = get_logger(__name__)

DB_PATH = "users.db"

def initialize_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                is_verified INTEGER DEFAULT 0,
                permissions TEXT DEFAULT '{}'
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("User database initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"DB Init Error: {str(e)}")
        return False

def register_user(email, username, password, full_name):
    try:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, username, password, full_name) VALUES (?, ?, ?, ?)",
                  (email, username, hashed_pw.decode(), full_name))
        conn.commit()
        conn.close()
        logger.info(f"User registered: {username}")
        return True, "Registration successful. Please verify your email."
    except sqlite3.IntegrityError as e:
        logger.warning(f"Registration error: {str(e)}")
        if "email" in str(e):
            return False, "Email already in use."
        elif "username" in str(e):
            return False, "Username already taken."
        return False, "Registration failed."
    except Exception as e:
        logger.error(f"Unexpected registration error: {str(e)}")
        return False, "An unexpected error occurred."

def authenticate_user(identifier, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, password, is_verified FROM users WHERE email = ? OR username = ?", (identifier, identifier))
        result = c.fetchone()
        conn.close()

        if result:
            user_id, hashed_pw, is_verified = result
            if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
                if is_verified:
                    logger.info(f"User authenticated: {identifier}")
                    return user_id
                else:
                    logger.warning(f"Email not verified for user: {identifier}")
                    return None
        logger.warning(f"Failed login for: {identifier}")
        return None
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None

def verify_email(token):
    try:
        # This is a mocked email verification for demo purposes
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET is_verified = 1 WHERE username = ?", (token,))
        conn.commit()
        conn.close()
        logger.info(f"Email verified for token: {token}")
        return True, "Email successfully verified!"
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False, "Email verification failed."

def initiate_password_reset(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE email = ?", (email,))
        result = c.fetchone()
        conn.close()
        if result:
            logger.info(f"Password reset initiated for {email}")
            return True  # Replace with actual email logic in prod
        return False
    except Exception as e:
        logger.error(f"Reset initiation failed: {str(e)}")
        return False

def complete_password_reset(username, new_password):
    try:
        hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, username))
        conn.commit()
        conn.close()
        logger.info(f"Password reset for {username}")
        return True
    except Exception as e:
        logger.error(f"Reset completion failed: {str(e)}")
        return False
