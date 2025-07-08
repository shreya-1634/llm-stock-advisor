import bcrypt
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import logging
from core.config import get_db_connection
import os
from typing import Tuple, Optional

# Initialize logger
logger = logging.getLogger(__name__)

def initialize_db() -> bool:
    """Initialize database tables with proper error handling"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash BYTEA NOT NULL,
                    full_name VARCHAR(100),
                    age INTEGER,
                    is_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR(100),
                    token_expires TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create password resets table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    token VARCHAR(100) UNIQUE,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using SMTP with error handling"""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv("SMTP_EMAIL")
        msg['To'] = to_email

        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def register_user(email: str, username: str, password: str, full_name: Optional[str] = None, age: Optional[int] = None) -> Tuple[bool, str]:
    """Complete user registration with validation"""
    # Input validation
    if not all([email, username, password]):
        return False, "All fields are required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check for existing user
            cur.execute("SELECT 1 FROM users WHERE email = %s OR username = %s", (email, username))
            if cur.fetchone():
                return False, "Email or username already exists"

            # Hash password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Generate verification token
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=24)
            
            # Insert new user
            cur.execute("""
                INSERT INTO users (email, username, password_hash, full_name, age, verification_token, token_expires)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (email, username, hashed_pw, full_name, age, token, expires))
            
            conn.commit()
            
            # Send verification email
            verification_link = f"http://localhost:8501/?verify={token}"
            email_body = f"""
                Welcome to Stock Advisor!

                Please verify your email by clicking:
                {verification_link}

                This link expires in 24 hours.
            """
            if send_email(email, "Verify Your Email", email_body):
                return True, "Registration successful! Check your email."
            return False, "Registration complete but email sending failed"
            
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        if conn:
            conn.rollback()
        return False, "Registration failed"
    finally:
        if conn:
            conn.close()

def verify_email(token: str) -> Tuple[bool, str]:
    """Verify user's email using token"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET is_verified = TRUE, 
                    verification_token = NULL,
                    token_expires = NULL
                WHERE verification_token = %s 
                AND token_expires > NOW()
                RETURNING email
            """, (token,))
            
            if cur.fetchone():
                conn.commit()
                return True, "Email verified successfully!"
            return False, "Invalid or expired verification link"
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False, "Verification failed"
    finally:
        if conn:
            conn.close()

def authenticate_user(identifier: str, password: str) -> Optional[int]:
    """Secure authentication with email or username"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, password_hash FROM users 
                WHERE (email = %s OR username = %s) 
                AND is_verified = TRUE
            """, (identifier, identifier))
            
            user = cur.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
                return user[0]
            return None
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def initiate_password_reset(email: str) -> bool:
    """Start password reset process"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                return True  # Don't reveal if email doesn't exist
            
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=1)
            
            cur.execute("""
                INSERT INTO password_resets (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user[0], token, expires))
            
            conn.commit()
            
            reset_link = f"http://localhost:8501/?reset={token}"
            email_body = f"""
                Password Reset Request:

                Click here to reset your password:
                {reset_link}

                This link expires in 1 hour.
            """
            return send_email(email, "Password Reset", email_body)
    except Exception as e:
        logger.error(f"Password reset initiation failed: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def complete_password_reset(token: str, new_password: str) -> bool:
    """Complete password reset process"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get valid reset request
            cur.execute("""
                SELECT user_id FROM password_resets
                WHERE token = %s AND expires_at > NOW()
            """, (token,))
            reset = cur.fetchone()
            if not reset:
                return False
            
            # Update password
            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cur.execute("""
                UPDATE users SET password_hash = %s
                WHERE id = %s
            """, (hashed_pw, reset[0]))
            
            # Delete used token
            cur.execute("""
                DELETE FROM password_resets
                WHERE token = %s
            """, (token,))
            
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
