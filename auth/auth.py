# auth/auth.py
from core.config import get_logger
import bcrypt

logger = get_logger(__name__)

# TEST USER DATABASE (pre-hashed passwords)
USERS = {
    "admin": {
        "password": b"$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGgaXNlK",  # admin123
        "permissions": ["view", "trade", "admin"]
    },
    "trader": {
        "password": b"$2b$12$W6G5hUO2d1vJ1AQR.6QZeuAhfz7X3xjK7rq9V9tVYJ9dKj6YbW5mK",  # trader123
        "permissions": ["view", "trade"]
    }
}

def authenticate_user(username: str, password: str) -> bool:
    """Working authentication with debug prints"""
    print(f"Auth attempt: {username}")  # Debug
    
    user = USERS.get(username.lower())  # Case-insensitive
    if not user:
        print(f"User {username} not found")  # Debug
        return False
    
    # Verify password against stored hash
    try:
        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            print("Authentication successful!")  # Debug
            return True
    except Exception as e:
        print(f"Password check failed: {e}")  # Debug
    
    print("Authentication failed")  # Debug
    return False

def logout_user():
    print("User logged out")  # Debug

def check_permission(username: str, permission: str) -> bool:
    return permission in USERS.get(username.lower(), {}).get("permissions", [])
