# your_project/utils/password_utils.py

import bcrypt

class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password using bcrypt."""
        # bcrypt.gensalt() generates a salt, bcrypt.hashpw uses it to hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verifies a plain-text password against a hashed password."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError:
            # This can happen if the hashed_password is not a valid bcrypt hash
            return False
