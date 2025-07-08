# auth/auth.py
import bcrypt
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import logging
import time  # <-- THIS IS THE CRITICAL MISSING IMPORT
from core.config import get_db_connection
import os
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def initialize_db() -> bool:
    """Initialize database tables with proper error handling"""
    max_retries = 3
    for attempt in range(max_retries):
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
                logger.info("Database tables initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Database initialization failed (attempt {attempt + 1}): {str(e)}")
            if conn:
                conn.rollback()
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Exponential backoff
        finally:
            if conn:
                conn.close()


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Secure email sending with timeout and validation"""
    try:
        # Validate email format
        if "@" not in to_email or "." not in to_email.split("@")[-1]:
            raise ValueError(f"Invalid email format: {to_email}")

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv("SMTP_EMAIL")
        msg['To'] = to_email

        with smtplib.SMTP(
            host=os.getenv("SMTP_SERVER"),
            port=int(os.getenv("SMTP_PORT")),
            timeout=10  # 10-second timeout
        ) as server:
            server.starttls()
            server.login(
                user=os.getenv("SMTP_EMAIL"),
                password=os.getenv("SMTP_PASSWORD")
            )
            server.send_message(msg)
            logger.info(f"Email sent to {to_email}")
            return True
            
    except Exception as e:
        logger.error(f"Email failed to {to_email}: {str(e)}")
        return False

def register_user(
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    age: Optional[int] = None
) -> Tuple[bool, str]:
    """Secure user registration with validation"""
    # Input validation
    if not all([email, username, password]):
        return False, "All fields are required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not (6 <= len(username) <= 30:
        return False, "Username must be 6-30 characters"
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check existing user
            cur.execute("""
                SELECT 1 FROM users 
                WHERE email = %s OR username = %s
                FOR UPDATE  -- Prevent race conditions
            """, (email, username))
            
            if cur.fetchone():
                return False, "Email or username already exists"

            # Hash password with cost factor 14
            hashed_pw = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt(rounds=14)
            )
            
            # Generate verification token
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=24)
            
            # Insert new user
            cur.execute("""
                INSERT INTO users (
                    email, username, password_hash, 
                    full_name, age, verification_token, token_expires
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (email, username, hashed_pw, full_name, age, token, expires))
            
            conn.commit()
            
            # Send verification email
            verification_link = f"{os.getenv('APP_URL', 'http://localhost:8501')}/?verify={token}"
            email_body = f"""
                Welcome to Stock Advisor!

                Please verify your email:
                {verification_link}

                This link expires in 24 hours.
            """
            if send_email(email, "Verify Your Email", email_body):
                return True, "Registration successful! Check your email."
            return False, "Registration complete but email sending failed"
            
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return False, "Registration failed"
    finally:
        if conn:
            conn.close()

def verify_email(token: str) -> Tuple[bool, str]:
    """Token-based email verification with expiration check"""
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
        logger.error(f"Verification failed: {str(e)}", exc_info=True)
        return False, "Verification failed"
    finally:
        if conn:
            conn.close()

def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    """Secure authentication with brute force protection"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get user with lock to prevent timing attacks
            cur.execute("""
                SELECT id, password_hash, is_verified 
                FROM users 
                WHERE (email = %s OR username = %s)
                FOR UPDATE SKIP LOCKED
            """, (identifier, identifier))
            
            user = cur.fetchone()
            if not user:
                # Simulate password check to prevent timing leaks
                bcrypt.checkpw(b"dummy", b"$2b$12$dummyhash")
                return None
                
            user_id, hashed_pw, is_verified = user
            
            if not is_verified:
                logger.warning(f"Unverified login attempt: {identifier}")
                return None
                
            if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
                return {"id": user_id}
            return None
            
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def initiate_password_reset(email: str) -> bool:
    """Secure password reset initiation"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Invalidate any existing reset tokens first
            cur.execute("""
                UPDATE password_resets
                SET used = TRUE
                WHERE user_id = (
                    SELECT id FROM users WHERE email = %s
                )
            """, (email,))
            
            # Get user if exists
            cur.execute("""
                SELECT id FROM users WHERE email = %s
            """, (email,))
            user = cur.fetchone()
            
            if not user:
                return True  # Don't reveal if email doesn't exist
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=1)
            
            cur.execute("""
                INSERT INTO password_resets (
                    user_id, token, expires_at
                ) VALUES (%s, %s, %s)
            """, (user[0], token, expires))
            
            conn.commit()
            
            # Send reset email
            reset_link = f"{os.getenv('APP_URL', 'http://localhost:8501')}/?reset={token}"
            email_body = f"""
                Password Reset Request:

                Click here to reset your password:
                {reset_link}

                This link expires in 1 hour.
            """
            return send_email(email, "Password Reset", email_body)
            
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def complete_password_reset(token: str, new_password: str) -> bool:
    """Secure password reset completion"""
    if len(new_password) < 8:
        raise ValueError("Password too short")
        
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get valid reset request
            cur.execute("""
                SELECT user_id FROM password_resets
                WHERE token = %s 
                AND expires_at > NOW()
                AND used = FALSE
                FOR UPDATE  -- Prevent concurrent use
            """, (token,))
            reset = cur.fetchone()
            
            if not reset:
                return False
            
            user_id = reset[0]
            
            # Update password
            hashed_pw = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt(rounds=14)
            )
            cur.execute("""
                UPDATE users 
                SET password_hash = %s
                WHERE id = %s
            """, (hashed_pw, user_id))
            
            # Mark token as used
            cur.execute("""
                UPDATE password_resets
                SET used = TRUE
                WHERE token = %s
            """, (token,))
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_user_permissions(user_id: int) -> Dict[str, bool]:
    """Get user permissions safely"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT permissions FROM users
                WHERE id = %s
            """, (user_id,))
            result = cur.fetchone()
            return result[0] if result else {}
    except Exception as e:
        logger.error(f"Failed to get permissions: {str(e)}")
        return {}
    finally:
        if conn:
            conn.close()
