import sqlite3
import hashlib
import json
import uuid
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import get_logger
import streamlit as st

logger = get_logger(__name__)

DB_PATH = "users.db"
TOKEN_EXPIRY_MINUTES = 30

# ---------------------- Hashing ---------------------- #

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ---------------------- Email Sender ---------------------- #

def send_email(recipient, subject, message):
    try:
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        sender_email = st.secrets["email"]["email"]
        sender_password = st.secrets["email"]["password"]

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())

        logger.info(f"Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Email failed to {recipient}: {e}")
        return False

# ---------------------- User Registration/Login ---------------------- #

def register_user(name, email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False, "User already exists"
    
    hashed_pw = hash_password(password)
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "verified": False,
        "tokens": {}
    }

    c.execute(
        "INSERT INTO users (name, email, password, verified, tokens) VALUES (?, ?, ?, ?, ?)",
        (name, email, hashed_pw, False, json.dumps({}))
    )
    conn.commit()
    conn.close()

    token = generate_verification_token(email)
    send_email(email, "Verify Your Email", f"Your verification token: {token}")
    logger.info(f"User {email} registered. Verification token sent.")
    return True, "Registered successfully. Verification email sent."

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password, verified FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_hash, verified = result
        if not verified:
            return False, "Email not verified"
        if verify_password(password, stored_hash):
            return True, "Login successful"
        else:
            return False, "Invalid password"
    return False, "User not found"

# ---------------------- Email Verification ---------------------- #

def generate_verification_token(email):
    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    tokens = json.loads(c.fetchone()[0] or '{}')
    tokens["email_verification"] = {"token": token, "expires_at": expiry.isoformat()}

    c.execute("UPDATE users SET tokens = ? WHERE email = ?", (json.dumps(tokens), email))
    conn.commit()
    conn.close()

    return token

def verify_email_token(email, token):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False

    tokens = json.loads(result[0])
    data = tokens.get("email_verification", {})
    if data.get("token") == token and datetime.now() < datetime.fromisoformat(data.get("expires_at", "")):
        c.execute("UPDATE users SET verified = ?, tokens = ? WHERE email = ?", (True, json.dumps(tokens), email))
        conn.commit()
        conn.close()
        logger.info(f"Email verified: {email}")
        return True

    conn.close()
    return False

# ---------------------- Password Reset ---------------------- #

def initiate_password_reset(email):
    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False

    tokens = json.loads(result[0] or '{}')
    tokens["password_reset"] = {"token": token, "expires_at": expiry.isoformat()}

    c.execute("UPDATE users SET tokens = ? WHERE email = ?", (json.dumps(tokens), email))
    conn.commit()
    conn.close()

    send_email(email, "Reset Your Password", f"Your password reset token is: {token}")
    logger.info(f"Password reset initiated for: {email}")
    return True

def complete_password_reset(email, token, new_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False

    tokens = json.loads(result[0])
    data = tokens.get("password_reset", {})
    if data.get("token") == token and datetime.now() < datetime.fromisoformat(data.get("expires_at", "")):
        hashed_pw = hash_password(new_password)
        del tokens["password_reset"]

        c.execute(
            "UPDATE users SET password = ?, tokens = ? WHERE email = ?",
            (hashed_pw, json.dumps(tokens), email)
        )
        conn.commit()
        conn.close()
        logger.info(f"Password reset successful for: {email}")
        return True

    conn.close()
    return False

# ---------------------- Cleanup Expired Tokens ---------------------- #

def cleanup_expired_tokens():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT email, tokens FROM users")
    rows = c.fetchall()

    for email, token_json in rows:
        tokens = json.loads(token_json or '{}')
        updated = False
        for key in list(tokens.keys()):
            if datetime.now() > datetime.fromisoformat(tokens[key].get("expires_at", "2100-01-01")):
                del tokens[key]
                updated = True
        if updated:
            c.execute("UPDATE users SET tokens = ? WHERE email = ?", (json.dumps(tokens), email))
    
    conn.commit()
    conn.close()
    logger.info("Expired tokens cleaned up")
