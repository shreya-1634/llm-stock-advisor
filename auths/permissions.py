import sqlite3
import json
from datetime import datetime, timedelta
from core.config import get_logger

logger = get_logger(__name__)
DB_PATH = "users.db"

def request_permission(username, action, ticker, amount):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT permissions FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        permissions = json.loads(result[0]) if result and result[0] else {}

        permission_id = f"{action}_{ticker}_{datetime.now().timestamp()}"
        permissions[permission_id] = {
            "action": action,
            "ticker": ticker,
            "amount": amount,
            "requested_at": str(datetime.now()),
            "expires_at": str(datetime.now() + timedelta(minutes=30)),
            "granted": False
        }

        c.execute("UPDATE users SET permissions = ? WHERE username = ?",
                  (json.dumps(permissions), username))
        conn.commit()
        conn.close()

        logger.info(f"Permission requested: {permission_id}")
        return permission_id
    except Exception as e:
        logger.error(f"Permission request error: {str(e)}")
        return None

def check_permission(permission_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT permissions FROM users")
        users = c.fetchall()
        conn.close()

        for _, perm_json in users:
            permissions = json.loads(perm_json)
            if permission_id in permissions:
                permission = permissions[permission_id]
                if permission['granted'] and datetime.now() < datetime.fromisoformat(permission['expires_at']):
                    return True
        return False
    except Exception as e:
        logger.error(f"Check permission error: {str(e)}")
        return False

def grant_permission(username, permission_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT permissions FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if not result:
            return False

        permissions = json.loads(result[0])
        if permission_id in permissions:
            permissions[permission_id]['granted'] = True
            c.execute("UPDATE users SET permissions = ? WHERE username = ?",
                      (json.dumps(permissions), username))
            conn.commit()
            conn.close()
            logger.info(f"Permission granted: {permission_id}")
            return True

        conn.close()
        return False
    except Exception as e:
        logger.error(f"Grant permission error: {str(e)}")
        return False
