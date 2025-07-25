import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load email credentials from .env file
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))


def send_otp_email(to_email, otp, purpose="verification"):
    try:
        subject = f"Your OTP for {purpose.capitalize()}"

        # Compose the email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        body = f"""
        Hello,

        Your OTP for {purpose.lower()} is: {otp}

        Please do not share this OTP with anyone.

        Regards,
        Your AI Finance Assistant
        """
        msg.attach(MIMEText(body, "plain"))

        # Send the email using SMTP
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"OTP sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False
