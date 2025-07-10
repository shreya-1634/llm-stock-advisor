import sqlite3
import uuid
import hashlib
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from core.config import get_logger
import streamlit as st

logger = get_logger(__name__)

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0,
            verified INTEGER DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expiry TEXT,
            permissions TEXT DEFAULT '{}'
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_email(to_email, subject, content):
    try:
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = int(st.secrets["email"]["smtp_port"])
        smtp_email = st.secrets["email"]["email"]
        smtp_password = st.secrets["email"]["password"]

        msg = MIMEText(content, "html")
        msg["Subject"] = subject
        msg["From"] = smtp_email
        msg["To"] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Email send failed: {str(e)}")

def register_user(name, email, password, is_admin=False):
    hashed_pw = hash_password(password)
    token = str(uuid.uuid4())

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (name, email, password, is_admin, verification_token) VALUES (?, ?, ?, ?, ?)',
                  (name, email, hashed_pw, int(is_admin), token))
        conn.commit()
        conn.close()

        link = f"{st.secrets['app']['base_url']}?verify_token={token}"
        html = f"<p>Hi {name},</p><p>Please verify your email by clicking the link below:</p><a href='{link}'>{link}</a>"
        send_email(email, "Verify your email", html)
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password, verified FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return row[1] == 1  # Must be verified
    return False

def get_user_info(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, is_admin FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    return row if row else (None, 0)

def verify_email(token):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE verification_token = ?', (token,))
    row = c.fetchone()
    if row:
        c.execute('UPDATE users SET verified = 1, verification_token = NULL WHERE id = ?', (row[0],))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def initiate_password_reset(email):
    token = str(uuid.uuid4())
    expiry = (datetime.now() + timedelta(minutes=30)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?', (token, expiry, email))
    conn.commit()
    conn.close()

    link = f"{st.secrets['app']['base_url']}?reset_token={token}"
    html = f"<p>Click the link below to reset your password:</p><a href='{link}'>{link}</a>"
    send_email(email, "Password Reset", html)

def complete_password_reset(token, new_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, reset_token_expiry FROM users WHERE reset_token = ?', (token,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False

    expiry = datetime.fromisoformat(row[1])
    if datetime.now() > expiry:
        conn.close()
        return False

    hashed = hash_password(new_password)
    c.execute('UPDATE users SET password = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?', (hashed, row[0]))
    conn.commit()
    conn.close()
    return True
