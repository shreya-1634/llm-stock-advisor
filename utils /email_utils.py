# your_project/utils/email_utils.py

import smtplib
from email.mime.text import MIMEText
import secrets
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

class EmailUtils:
    def __init__(self):
        self.sender_email = os.getenv("EMAIL_USERNAME")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("EMAIL_HOST")
        self.smtp_port = int(os.getenv("EMAIL_PORT", 587)) # Default to 587 if not set

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generates a random numeric OTP."""
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    def send_verification_email(self, recipient_email: str, otp: str) -> bool:
        """Sends an email with the verification OTP."""
        if not all([self.sender_email, self.sender_password, self.smtp_server, self.smtp_port]):
            print("Error: Email configuration missing in .env. Cannot send email.")
            return False

        msg = MIMEText(f"Your email verification OTP is: {otp}\n\nThis OTP is valid for 5 minutes.")
        msg['Subject'] = "Your AI Stock Advisor Email Verification OTP"
        msg['From'] = self.sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls() # Secure the connection
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print(f"Verification email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send verification email to {recipient_email}: {e}")
            return False

    def send_password_reset_email(self, recipient_email: str, reset_link: str) -> bool:
        """Sends an email with a password reset link."""
        if not all([self.sender_email, self.sender_password, self.smtp_server, self.smtp_port]):
            print("Error: Email configuration missing in .env. Cannot send email.")
            return False

        msg = MIMEText(f"You requested a password reset for your AI Stock Advisor account.\n\n"
                       f"Please click on the following link to reset your password: {reset_link}\n\n"
                       f"If you did not request this, please ignore this email.")
        msg['Subject'] = "AI Stock Advisor Password Reset"
        msg['From'] = self.sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls() # Secure the connection
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print(f"Password reset email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send password reset email to {recipient_email}: {e}")
            return False
