import sqlite3
from datetime import datetime, timedelta
import json
from core.config import get_logger

logger = get_logger(__name__)

def request_permission(username, action, ticker, amount):
    conn = sqlite3.connect('users.db')
    try:
        c = conn.cursor()
        c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        permissions = json.loads(result[0]) if result and result[0] else {}
        
        permission_id = f"{action}_{ticker}_{datetime.now().timestamp()}"
        permissions[permission_id] = {
            'action': action,
            'ticker': ticker,
            'amount': amount,
            'requested_at': str(datetime.now()),
            'expires_at': str(datetime.now() + timedelta(minutes=30)),
            'granted': False
        }
        
        c.execute('UPDATE users SET permissions = ? WHERE username = ?',
                  (json.dumps(permissions), username))
        conn.commit()
        logger.info(f"Permission requested: {permission_id}")
        return permission_id
    except Exception as e:
        logger.error(f"Permission request failed: {str(e)}")
        raise
    finally:
        conn.close()

def check_permission(permission_id):
    conn = sqlite3.connect('users.db')
    try:
        c = conn.cursor()
        c.execute('SELECT username, permissions FROM users')
        users = c.fetchall()
        
        for username, perm_json in users:
            permissions = json.loads(perm_json)
            if permission_id in permissions:
                permission = permissions[permission_id]
                if permission['granted'] and datetime.now() < datetime.fromisoformat(permission['expires_at']):
                    logger.debug(f"Permission valid: {permission_id}")
                    return True
        logger.warning(f"Permission invalid/expired: {permission_id}")
        return False
    except Exception as e:
        logger.error(f"Permission check failed: {str(e)}")
        return False
    finally:
        conn.close()

def grant_permission(username, permission_id):
    conn = sqlite3.connect('users.db')
    try:
        c = conn.cursor()
        c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if not result:
            logger.error(f"User not found: {username}")
            return False
        
        permissions = json.loads(result[0])
        if permission_id in permissions:
            permissions[permission_id]['granted'] = True
            c.execute('UPDATE users SET permissions = ? WHERE username = ?',
                      (json.dumps(permissions), username))
            conn.commit()
            logger.info(f"Permission granted: {permission_id}")
            return True
        logger.error(f"Permission not found: {permission_id}")
        return False
    except Exception as e:
        logger.error(f"Permission grant failed: {str(e)}")
        return False
    finally:
        conn.close()
