# auth/auth.py (with fallback)
try:
    import bcrypt
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    def check_password(hashed, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
except ImportError:
    import hashlib
    import secrets
    def hash_password(password):
        salt = secrets.token_hex(8)
        return f"{salt}${hashlib.sha256((password + salt).encode()).hexdigest()}".encode()
    def check_password(hashed, password):
        salt, stored_hash = hashed.decode().split('$')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
        
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from core.config import get_db_connection, get_logger

logger = get_logger(__name__)

# Email configuration (update with your SMTP details)
SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "email": "your.email@gmail.com",
    "password": "your-app-password"  # Use app-specific password
}

def initialize_db():
    """Create database tables if they don't exist"""
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
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    finally:
        conn.close()

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_CONFIG["email"]
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Email failed to {to_email}: {str(e)}")
        return False

def register_user(email, username, password, full_name=None):
    """Register new user with email verification"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check existing user
            cur.execute("SELECT 1 FROM users WHERE email = %s OR username = %s", (email, username))
            if cur.fetchone():
                return False, "Email or username already exists"

            # Hash password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Generate verification token
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=24)
            
            # Insert user
            cur.execute("""
                INSERT INTO users (email, username, password_hash, full_name, verification_token, token_expires)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, username, hashed_pw, full_name, token, expires))
            
            conn.commit()
            
            # Send verification email
            verification_link = f"http://yourdomain.com/?verify={token}"
            email_body = f"""
                Welcome to Stock Advisor!
                
                Please verify your email by clicking:
                {verification_link}
                
                This link expires in 24 hours.
            """
            if send_email(email, "Verify Your Email", email_body):
                return True, "Registration successful! Check your email to verify."
            return False, "Registration complete but failed to send verification email"
    except Exception as e:
        conn.rollback()
        logger.error(f"Registration failed: {str(e)}")
        return False, "Registration failed"
    finally:
        conn.close()

def verify_email(token):
    """Verify user's email using token"""
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
                RETURNING email
            """, (token,))
            
            if cur.fetchone():
                conn.commit()
                return True, "Email verified successfully!"
            return False, "Invalid or expired verification link"
    finally:
        conn.close()

def authenticate_user(identifier, password):
    """Authenticate user with email/username and password"""
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
                return user[0]
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
                return True  # Don't reveal if email doesn't exist
            
            token = secrets.token_urlsafe(32)
            expires = datetime.now() + timedelta(hours=1)
            
            cur.execute("""
                INSERT INTO password_resets (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user[0], token, expires))
            
            conn.commit()
            
            reset_link = f"http://yourdomain.com/?reset={token}"
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
    """Complete password reset"""
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
    finally:
        conn.close()
