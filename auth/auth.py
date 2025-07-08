import bcrypt
import re
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from core.config import get_logger, get_db_connection
from core.security import generate_token, validate_token

logger = get_logger(__name__)

# Email configuration (replace with your SMTP details)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your.email@gmail.com"
EMAIL_PASSWORD = "your-email-password"

def initialize_db():
    """Create necessary tables if they don't exist"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
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
                );
                CREATE TABLE IF NOT EXISTS password_resets (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    token VARCHAR(100) UNIQUE,
                    expires_at TIMESTAMP NOT NULL
                );
            """)
        conn.commit()
    finally:
        conn.close()

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def register_user(email, username, password, full_name=None, age=None):
    """Register a new user with email verification"""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if email or username exists
            cur.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (email, username)
            )
            if cur.fetchone():
                return False, "Email or username already exists"

            # Hash password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)

            # Generate verification token
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=24)

            # Insert new user
            cur.execute("""
                INSERT INTO users (email, username, password_hash, full_name, age, verification_token, token_expires)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (email, username, hashed_pw, full_name, age, token, expires))

            user_id = cur.fetchone()[0]
            conn.commit()

            # Send verification email
            verification_link = f"http://yourapp.com/verify?token={token}"
            email_body = f"""
                Welcome to Stock Advisor!
                Please verify your email by clicking:
                {verification_link}
                This link expires in 24 hours.
            """
            send_email(email, "Verify Your Email", email_body)

            return True, "Registration successful! Check your email to verify."
    except Exception as e:
        conn.rollback()
        logger.error(f"Registration failed: {str(e)}")
        return False, "Registration failed"
    finally:
        conn.close()

def verify_email(token):
    """Verify user email using token"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET is_verified = TRUE, 
                    verification_token = NULL,
                    token_expires = NULL
                WHERE verification_token = %s 
                AND token_expires > NOW()
                RETURNING id
            """, (token,))
            
            if cur.fetchone():
                conn.commit()
                return True, "Email verified successfully!"
            return False, "Invalid or expired token"
    finally:
        conn.close()

def authenticate_user(identifier, password):
    """Authenticate using email or username"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, password_hash FROM users 
                WHERE (email = %s OR username = %s) 
                AND is_verified = TRUE
            """, (identifier, identifier))
            
            user = cur.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
                return user[0]  # Return user ID
            return None
    finally:
        conn.close()

def initiate_password_reset(email):
    """Start password reset process"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                return False  # Don't reveal if email exists
            
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=1)
            
            cur.execute("""
                INSERT INTO password_resets (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user[0], token, expires))
            
            conn.commit()
            
            reset_link = f"http://yourapp.com/reset-password?token={token}"
            email_body = f"""
                Password Reset Request:
                Click here to reset your password:
                {reset_link}
                This link expires in 1 hour.
            """
            return send_email(email, "Password Reset", email_body)
    finally:
        conn.close()

def complete_password_reset(token, new_password):
    """Finish password reset process"""
    conn = get_db_connection()
    try:
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
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
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
    finally:
        conn.close()
