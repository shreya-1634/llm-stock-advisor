# your_project/utils/role_utils.py

# This file currently doesn't hold much independent logic
# as permissions are handled directly in auths/permissions.py
# and checked via utils/session_utils.py.

# You could use this file in the future for:
# - More complex role hierarchy management
# - Functions to assign/change user roles (would interact with db/user_manager.py)
# - Utilities for displaying role-specific UI elements.

# For now, it can remain largely empty or removed.
# from auths.permissions import Permissions

# class RoleUtils:
#     @staticmethod
#     def get_display_name(role: str) -> str:
#         """Returns a user-friendly display name for a role."""
#         return role.replace('_', ' ').title()

#     @staticmethod
#     def list_available_roles() -> list:
#         """Returns a list of all defined roles."""
#         return list(Permissions.ROLES.keys())

# Example usage in app.py if you had complex role management:
# st.sidebar.write(f"Role: **{RoleUtils.get_display_name(session_manager.get_current_user_role())}**")
