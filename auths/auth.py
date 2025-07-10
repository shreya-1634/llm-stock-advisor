import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from core.config import get_logger

load_dotenv()
logger = get_logger(__name__)
DB_FILE = "users.db"

# ========== Secret Getter ==========
def get_secret(key, category="email"):
    try:
        return st.secrets[category][key]
    except:
        return os.getenv(key.upper())

# ========== Email Sender ==========
def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = get_secret("email", "email")
        msg["To"] = to

        with smtplib.SMTP(get_secret("smtp_server", "email"), int(get_secret("smtp_port", "email"))) as server:
            server.starttls()
            server.login(get_secret("email", "email"), get_secret("password", "email"))
            server.send_message(msg)

        logger.info(f"Email sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

# ========== Utility ==========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ========== Registration ==========
def register_user(username, email, password):
    try:
        hashed = hash_password(password)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # ✅ Create table if it doesn't exist
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

        # ✅ Insert new user
        c.execute("""
            INSERT INTO users (username, email, password, verified, permissions, tokens)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, hashed, False, json.dumps({}), json.dumps({})))

        conn.commit()
        conn.close()
        logger.info(f"User registered: {username}")
        send_email(email, "Verify your email", f"Your verification token is: {generate_verification_token(email)}")
        return True, "User registered successfully. Verification email sent."

    except sqlite3.IntegrityError:
        return False, "Email already registered."


# ========== Authentication ==========
def authenticate_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()

    if row and verify_password(password, row[2]):
        if not bool(row[3]):
            return None  # Not verified
        return {
            "username": row[0],
            "email": row[1],
            "verified": bool(row[3]),
            "permissions": json.loads(row[4] or "{}"),
            "tokens": json.loads(row[5] or "{}")
        }
    return None

# ========== Email Verification ==========
def generate_verification_token(email):
    token = secrets.token_hex(3)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    tokens = json.loads(result[0]) if result and result[0] else {}

    tokens["verification"] = {
        "token": token,
        "created_at": str(datetime.now())
    }

    c.execute("UPDATE users SET tokens = ? WHERE email = ?", (json.dumps(tokens), email))
    conn.commit()
    conn.close()
    return token

def verify_email(email, token_input):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False

    tokens = json.loads(result[0] or "{}")
    token_data = tokens.get("verification")
    if not token_data:
        conn.close()
        return False

    token = token_data["token"]
    created_at = datetime.fromisoformat(token_data["created_at"])

    if token_input == token and datetime.now() - created_at < timedelta(minutes=30):
        c.execute("UPDATE users SET verified = ?, tokens = ? WHERE email = ?", (True, json.dumps({}), email))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

# ========== Password Reset ==========
def initiate_password_reset(email):
    token = secrets.token_hex(4)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    tokens = json.loads(result[0]) if result and result[0] else {}

    tokens["reset"] = {
        "token": token,
        "created_at": str(datetime.now())
    }

    c.execute("UPDATE users SET tokens = ? WHERE email = ?", (json.dumps(tokens), email))
    conn.commit()
    conn.close()

    send_email(email, "Password Reset Token", f"Use this token to reset your password: {token}")
    return token

def complete_password_reset(email, token_input, new_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False

    tokens = json.loads(result[0] or "{}")
    token_data = tokens.get("reset")
    if not token_data:
        conn.close()
        return False

    token = token_data["token"]
    created_at = datetime.fromisoformat(token_data["created_at"])

    if token_input == token and datetime.now() - created_at < timedelta(minutes=30):
        hashed = hash_password(new_password)
        tokens.pop("reset", None)
        c.execute("UPDATE users SET password = ?, tokens = ? WHERE email = ?", (hashed, json.dumps(tokens), email))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

# ========== Streamlit Session ==========
def logout_user():
    if 'user' in st.session_state:
        del st.session_state['user']

def get_logged_in_user():
    return st.session_state.get("user", None)
