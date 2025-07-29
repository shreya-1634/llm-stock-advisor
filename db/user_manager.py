# your_project/db/user_manager.py

import sqlite3
import json
import time
import os # This import statement should always be at the top of the file
from typing import Dict, Any, Optional

class UserManager:
    def __init__(self, db_path: str = 'data/users.db'):
        self.db_path = db_path
        self._ensure_db_dir()
        self._create_tables()

    def _ensure_db_dir(self):
        """Ensures the directory for the database file exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_db_connection(self):
        """Establishes and returns a SQLite database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name (e.g., row['email'])
        return conn

    def _create_tables(self):
        """Creates the necessary tables if they do not already exist."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Table for storing user registration data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                role TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''') # <-- Ensure this closing triple quote is exactly here

        # Table for storing One-Time Passwords (OTPs) for email verification/password reset
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otps (
                email TEXT NOT NULL UNIQUE,
                otp_code TEXT NOT NULL,
                expiry_time INTEGER NOT NULL,
                FOREIGN KEY (email) REFERENCES users (email) ON DELETE CASCADE
            )
        ''') # <-- Ensure this closing triple quote is exactly here

        # Table for logging user activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''') # <-- Ensure this closing triple quote is exactly here

        conn.commit()
        conn.close()

    def add_user(self, email: str, password_hash: str, role: str = 'free') -> bool:
        """Adds a new user to the database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                           (email, password_hash, role))
            conn.commit()
            self._log_activity(email, "signup", "User registered successfully.")
            return True
        except sqlite3.IntegrityError: # User with this email already exists (UNIQUE constraint violation)
            return False
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves user data by email."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone() # Fetch one row
        conn.close()
        return dict(user_data) if user_data else None

    def update_user_password(self, email: str, new_password_hash: str) -> bool:
        """Updates a user's password in the database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_password_hash, email))
        conn.commit()
        updated = cursor.rowcount > 0 # Check if any rows were affected
        if updated:
            self._log_activity(email, "password_reset", "User password updated.")
        conn.close()
        return updated

    def set_email_verified(self, email: str, status: bool) -> bool:
        """Sets the email verification status for a user."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified = ? WHERE email = ?", (status, email))
        conn.commit()
        updated = cursor.rowcount > 0
        if updated and status:
            self._log_activity(email, "email_verification", "Email verified.")
        conn.close()
        return updated

    def store_otp(self, email: str, otp_code: str, expiry_minutes: int = 5) -> bool:
        """Stores an OTP for a user, replacing any existing OTP."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        expiry_time = int(time.time()) + (expiry_minutes * 60)
        try:
            # Use INSERT OR REPLACE to update OTP if user already has one
            cursor.execute("INSERT OR REPLACE INTO otps (email, otp_code, expiry_time) VALUES (?, ?, ?)",
                           (email, otp_code, expiry_time))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing OTP for {email}: {e}")
            return False
        finally:
            conn.close()

    def verify_otp(self, email: str, otp_code: str) -> bool:
        """Verifies an OTP for a user and invalidates it if successful."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code, expiry_time FROM otps WHERE email = ?", (email,))
        otp_data = cursor.fetchone()
        if otp_data:
            stored_otp, expiry_time = otp_data['otp_code'], otp_data['expiry_time']
            if stored_otp == otp_code and expiry_time > int(time.time()):
                # OTP is valid and not expired, delete it as it's used
                cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
                conn.commit()
                conn.close()
                return True
        conn.close()
        return False

    def _log_activity(self, user_email: str, activity_type: str, details: Optional[str] = None):
        """Logs user activity in the database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO activity_logs (user_email, activity_type, details) VALUES (?, ?, ?)",
                           (user_email, activity_type, details))
            conn.commit()
        except Exception as e:
            print(f"Error logging activity for {user_email}: {e}")
        finally:
            conn.close()

    def get_user_activity(self, user_email: str, limit: int = 10) -> list:
        """Retrieves a list of recent activities for a user."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activity_logs WHERE user_email = ? ORDER BY timestamp DESC LIMIT ?",
                       (user_email, limit))
        logs = [dict(row) for row in cursor.fetchall()] # Convert rows to dictionaries
        conn.close()
        return logs
