import bcrypt
from core.config import get_logger

logger = get_logger(__name__)

# Hashed password database (demo purposes)
USERS = {
    "admin": {
        # Password: "admin123"
        "password": b"$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGgaXNlK",
        "permissions": ["view", "trade", "admin"]
    },
    "trader": {
        # Password: "trader123"
        "password": b"$2b$12$W6G5hUO2d1vJ1AQR.6QZeuAhfz7X3xjK7rq9V9tVYJ9dKj6YbW5mK",
        "permissions": ["view", "trade"]
    }
}

def authenticate_user(username: str, password: str) -> bool:
    """Secure authentication with bcrypt hashing"""
    try:
        user = USERS.get(username)
        if user:
            # Verify password against hashed version
            if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
                logger.info(f"Successful login for {username}")
                return True
        logger.warning(f"Failed login attempt for {username}")
        return False
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        return False

def logout_user():
    """Handle logout cleanup"""
    logger.info("User logged out")

def check_permission(username: str, permission: str) -> bool:
    """Check user permissions"""
    return permission in USERS.get(username, {}).get("permissions", [])
