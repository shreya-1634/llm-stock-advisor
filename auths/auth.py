import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from core.config import get_logger
import smtplib
from email.mime.text import MIMEText
import streamlit as st
import os

logger = get_logger(__name__)
DB_FILE = "users.db"

# ------------------------------------
# Hashing & Verification Utilities
# ------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ------------------------------------
# Email Sender
# ------------------------------------
def send_email(to, subject, body):
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("EMAIL")
        sender_password = os.getenv("EMAIL_PASSWORD")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        logger.info(f"Email sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

# ------------------------------------
# User Registration
# ------------------------------------
def register_user(username, email, password):
    try:
        hashed = hash_password(password)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (username, email, password, verified, permissions, tokens)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, hashed, False, json.dumps({}), json.dumps({})))
        conn.commit()
        conn.close()

        token = generate_verification_token(email)
        send_email(email, "Verify your email", f"Your verification token is: {token}")
        logger.info(f"User registered: {username}")
        return True, "User registered successfully. Verification email sent."
    except sqlite3.IntegrityError:
        return False, "Email already registered."

# ------------------------------------
# User Authentication
# ------------------------------------
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

# ------------------------------------
# Verification Token Generation
# ------------------------------------
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
    logger.info(f"Verification token generated for {email}")
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
        logger.info(f"User verified: {email}")
        return True

    conn.close()
    return False

# ------------------------------------
# Password Reset
# ------------------------------------
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
    logger.info(f"Password reset token sent to {email}")
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
        tokens.pop("reset")
        c.execute("UPDATE users SET password = ?, tokens = ? WHERE email = ?", (hashed, json.dumps(tokens), email))
        conn.commit()
        conn.close()
        logger.info(f"Password reset successful for {email}")
        return True

    conn.close()
    return False

# ------------------------------------
# Streamlit State Helpers
# ------------------------------------
def logout_user():
    if 'user' in st.session_state:
        del st.session_state.user

def get_logged_in_user():
    return st.session_state.get("user", None)
