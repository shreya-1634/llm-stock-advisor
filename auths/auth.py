# auths/auth.py

import sqlite3
import hashlib
import secrets
import json
import os
import streamlit as st
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import smtplib
from core.config import get_logger

logger = get_logger(__name__)
DB_FILE = "users.db"
TOKEN_EXPIRY_MINUTES = 30

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def send_email(to: str, subject: str, body: str) -> bool:
    try:
        smtp_server = os.getenv("EMAIL_USER")  # no, it's EMAIL_USER used in config? fix: SMTP_SERVER env
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender = os.getenv("EMAIL") or os.getenv("EMAIL_USER")
        sender_pw = os.getenv("EMAIL_PASSWORD")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, sender_pw)
            server.send_message(msg)
        logger.info(f"Sent email to {to}")
        return True
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return False

def _connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def _cleanup_expired_tokens(tokens: dict) -> dict:
    cleaned = {}
    now = datetime.now()
    for ttype, data in tokens.items():
        created = datetime.fromisoformat(data.get("created_at"))
        if now - created < timedelta(minutes=TOKEN_EXPIRY_MINUTES):
            cleaned[ttype] = data
    return cleaned

def register_user(username: str, email: str, password: str):
    hashed = hash_password(password)
    conn = _connect()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(username,email,password,verified,permissions,tokens) VALUES (?,?,?,?,?,?)",
                  (username, email, hashed, False, json.dumps({}), json.dumps({})))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False, "❌ Email already registered."
    token = _generate_token(email, "verification")
    send_email(email, "Verify your email", f"Your verification token: {token}")
    conn.close()
    logger.info(f"Registered {username}, verification token sent")
    return True, "✅ Registered successfully. Check your email for verification code."

def _generate_token(email: str, ttype: str) -> str:
    token = secrets.token_hex(3)
    conn = _connect(); c=conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email=?", (email,))
    row = c.fetchone()
    tokens = json.loads(row["tokens"] or "{}") if row else {}
    tokens = _cleanup_expired_tokens(tokens)
    tokens[ttype] = {"token": token, "created_at": str(datetime.now())}
    c.execute("UPDATE users SET tokens=? WHERE email=?", (json.dumps(tokens), email))
    conn.commit(); conn.close()
    logger.info(f"Generated {ttype} token for {email}")
    return token

def verify_email(email: str, token_input: str) -> bool:
    conn = _connect(); c=conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email=?", (email,))
    row = c.fetchone()
    if not row:
        conn.close(); return False
    tokens = json.loads(row["tokens"] or "{}")
    tokens = _cleanup_expired_tokens(tokens)
    v = tokens.get("verification")
    if v and v.get("token") == token_input:
        c.execute("UPDATE users SET verified=?, tokens=? WHERE email=?", (True, json.dumps({}), email))
        conn.commit(); conn.close()
        logger.info(f"{email} verified")
        return True
    conn.close()
    return False

def authenticate_user(email: str, password: str):
    conn = _connect(); c=conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row and verify_password(password, row["password"]):
        if not row["verified"]:
            return None
        return {
            "username": row["username"],
            "email": row["email"],
            "verified": bool(row["verified"]),
            "permissions": json.loads(row["permissions"] or "{}"),
            "tokens": json.loads(row["tokens"] or "{}"),
        }
    return None

def initiate_password_reset(email: str) -> bool:
    conn = _connect(); c=conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if not c.fetchone():
        conn.close(); return False
    token = _generate_token(email, "reset")
    send_email(email, "Password reset token", f"Use this token to reset your password: {token}")
    conn.close()
    logger.info(f"Sent password reset to {email}")
    return True

def complete_password_reset(email: str, token_input: str, new_password: str) -> bool:
    conn = _connect(); c=conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email=?", (email,))
    row = c.fetchone()
    if not row:
        conn.close(); return False
    tokens = json.loads(row["tokens"] or "{}")
    tokens = _cleanup_expired_tokens(tokens)
    r = tokens.get("reset")
    if r and r.get("token") == token_input:
        hashed = hash_password(new_password)
        tokens.pop("reset", None)
        c.execute("UPDATE users SET password=?, tokens=? WHERE email=?", (hashed, json.dumps(tokens), email))
        conn.commit(); conn.close()
        logger.info(f"Password reset for {email}")
        return True
    conn.close()
    return False

def logout_user():
    if "user" in st.session_state:
        del st.session_state["user"]

def get_logged_in_user():
    return st.session_state.get("user", None)
