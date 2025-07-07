from datetime import datetime, timedelta
import json
import sqlite3

def request_permission(username, action, ticker, amount):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get current permissions
    c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    permissions = json.loads(result[0]) if result and result[0] else {}
    
    # Create new permission
    permission_id = f"{action}_{ticker}_{datetime.now().timestamp()}"
    permissions[permission_id] = {
        'action': action,
        'ticker': ticker,
        'amount': amount,
        'requested_at': str(datetime.now()),
        'expires_at': str(datetime.now() + timedelta(minutes=30)),
        'granted': False
    }
    
    # Update database
    c.execute('UPDATE users SET permissions = ? WHERE username = ?',
              (json.dumps(permissions), username))
    conn.commit()
    conn.close()
    
    return permission_id

def check_permission(permission_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Find user with this permission
    c.execute('SELECT username, permissions FROM users')
    users = c.fetchall()
    
    for username, perm_json in users:
        permissions = json.loads(perm_json)
        if permission_id in permissions:
            permission = permissions[permission_id]
            if permission['granted'] and datetime.now() < datetime.fromisoformat(permission['expires_at']):
                conn.close()
                return True
    
    conn.close()
    return False

def grant_permission(username, permission_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('SELECT permissions FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False
    
    permissions = json.loads(result[0])
    if permission_id in permissions:
        permissions[permission_id]['granted'] = True
        c.execute('UPDATE users SET permissions = ? WHERE username = ?',
                  (json.dumps(permissions), username))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False
