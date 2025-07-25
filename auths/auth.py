import json
import os
import bcrypt
import random
import string
from datetime import datetime, timedelta

from email_utils import send_otp_email

USER_DB_FILE = "data/users.json"
OTP_STORE_FILE = "data/otp_store.json"


def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_otps():
    if not os.path.exists(OTP_STORE_FILE):
        return {}
    with open(OTP_STORE_FILE, "r") as f:
        return json.load(f)


def save_otps(otps):
    with open(OTP_STORE_FILE, "w") as f:
        json.dump(otps, f, indent=4)


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def signup_user(email, password):
    users = load_users()
    if email in users:
        return {"success": False, "message": "User already exists."}

    hashed_password = hash_password(password)
    users[email] = {
        "password": hashed_password,
        "verified": False,
        "created_at": datetime.utcnow().isoformat()
    }
    save_users(users)

    otp = generate_otp()
    otps = load_otps()
    otps[email] = {
        "otp": otp,
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    }
    save_otps(otps)
    send_otp_email(email, otp)

    return {"success": True, "message": "Signup successful. OTP sent for email verification."}


def verify_email(email, entered_otp):
    otps = load_otps()
    if email not in otps:
        return {"success": False, "message": "No OTP found."}

    otp_entry = otps[email]
    if datetime.utcnow() > datetime.fromisoformat(otp_entry["expires_at"]):
        return {"success": False, "message": "OTP expired."}

    if otp_entry["otp"] != entered_otp:
        return {"success": False, "message": "Incorrect OTP."}

    users = load_users()
    if email in users:
        users[email]["verified"] = True
        save_users(users)

    del otps[email]
    save_otps(otps)

    return {"success": True, "message": "Email verified successfully."}


def login_user(email, password):
    users = load_users()
    user = users.get(email)
    if not user:
        return {"success": False, "message": "User not found."}
    if not user.get("verified"):
        return {"success": False, "message": "Email not verified."}
    if not check_password(password, user["password"]):
        return {"success": False, "message": "Incorrect password."}
    return {"success": True, "message": "Login successful."}


def send_password_reset(email):
    users = load_users()
    if email not in users:
        return {"success": False, "message": "User not found."}

    otp = generate_otp()
    otps = load_otps()
    otps[email] = {
        "otp": otp,
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    }
    save_otps(otps)
    send_otp_email(email, otp)

    return {"success": True, "message": "OTP sent for password reset."}


def reset_password(email, entered_otp, new_password):
    otps = load_otps()
    if email not in otps:
        return {"success": False, "message": "No OTP found."}

    otp_entry = otps[email]
    if datetime.utcnow() > datetime.fromisoformat(otp_entry["expires_at"]):
        return {"success": False, "message": "OTP expired."}

    if otp_entry["otp"] != entered_otp:
        return {"success": False, "message": "Incorrect OTP."}

    users = load_users()
    if email in users:
        users[email]["password"] = hash_password(new_password)
        save_users(users)

    del otps[email]
    save_otps(otps)

    return {"success": True, "message": "Password reset successfully."}

def verify_token(token):
    try:
        email = serializer.loads(token, max_age=3600)  # 1 hour token
        return {"status": True, "email": email}
    except SignatureExpired:
        return {"status": False, "message": "Token expired."}
    except BadSignature:
        return {"status": False, "message": "Invalid token."}
