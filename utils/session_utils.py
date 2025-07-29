# your_project/utils/session_utils.py

import streamlit as st
import os
import secrets
from dotenv import load_dotenv
from auths.permissions import Permissions
from typing import Optional

load_dotenv() # Load environment variables

class SessionManager:
    def __init__(self):
        # Initialize session state variables if they don't exist
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
        if 'user_email' not in st.session_state:
            st.session_state['user_email'] = None
        if 'user_role' not in st.session_state:
            st.session_state['user_role'] = 'guest' # Default role for non-logged-in users

        # Ensure a secret key for session state if running locally without explicit config
        if "SESSION_SECRET_KEY" not in os.environ and "streamlit" not in st.__main__.__dict__:
            # This check prevents re-generating key on every rerun in deployed apps
            # but ensures it exists for local dev if not in .env
            if not st.session_state.get('_secret_key_generated'):
                st.session_state['_secret_key_generated'] = secrets.token_hex(32)
                os.environ["STREAMLIT_SERVER_COOKIE_SECRET"] = st.session_state['_secret_key_generated']
        elif "SESSION_SECRET_KEY" in os.environ:
             os.environ["STREAMLIT_SERVER_COOKIE_SECRET"] = os.getenv("SESSION_SECRET_KEY")


    def login_user(self, email: str, role: str = 'free'):
        """Logs in a user by setting session state variables."""
        st.session_state['logged_in'] = True
        st.session_state['user_email'] = email
        st.session_state['user_role'] = role
        st.success(f"Welcome, {email}!")

    def logout_user(self):
        """Logs out the current user and clears session state related to login."""
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = None
        st.session_state['user_role'] = 'guest'
        st.info("You have been logged out.")

    def is_logged_in(self) -> bool:
        """Checks if a user is currently logged in."""
        return st.session_state.get('logged_in', False)

    def get_current_user_email(self) -> Optional[str]:
        """Returns the email of the currently logged-in user, or None if not logged in."""
        return st.session_state.get('user_email')

    def get_current_user_role(self) -> str:
        """Returns the role of the currently logged-in user, defaulting to 'guest'."""
        return st.session_state.get('user_role', 'guest')

    def has_permission(self, feature_name: str) -> bool:
        """Checks if the current user's role has permission for a specific feature."""
        current_role = self.get_current_user_role()
        return Permissions.check_permission(current_role, feature_name)
