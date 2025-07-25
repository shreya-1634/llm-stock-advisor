import json
import os

PERMISSIONS_FILE = "data/permissions.json"

# Default permission structure
DEFAULT_PERMISSIONS = {
    "can_fetch_data": True,
    "can_see_charts": True,
    "can_view_indicators": True,
    "can_view_news": True,
    "can_predict_prices": True,
    "can_view_volatility": True,
    "can_get_recommendation": True,
    "can_use_ai_trading": False  # Admin or Pro users only
}


def load_permissions():
    if not os.path.exists(PERMISSIONS_FILE):
        return {}
    with open(PERMISSIONS_FILE, "r") as f:
        return json.load(f)


def save_permissions(permissions):
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(permissions, f, indent=4)


def initialize_user_permissions(email):
    permissions = load_permissions()
    if email not in permissions:
        permissions[email] = DEFAULT_PERMISSIONS
        save_permissions(permissions)


def get_user_permissions(email):
    permissions = load_permissions()
    return permissions.get(email, DEFAULT_PERMISSIONS)


def update_user_permission(email, key, value):
    permissions = load_permissions()
    if email in permissions:
        permissions[email][key] = value
        save_permissions(permissions)


def check_permission(email, permission_key):
    user_permissions = get_user_permissions(email)
    return user_permissions.get(permission_key, False)


# For Streamlit UI or backend decisions
def require_permission(email, permission_key, feature_name):
    if not check_permission(email, permission_key):
        return f"🚫 You do not have permission to use '{feature_name}'"
    return None
