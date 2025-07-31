# your_project/utils/session_utils.py

import streamlit as st
import os
import secrets
from dotenv import load_dotenv
from auths.permissions import Permissions
from typing import Optional # <--- ADDED

load_dotenv() # Load environment variables

class SessionManager:
    def __init__(self):
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
        if 'user_email' not in st.session_state:
            st.session_state['user_email'] = None
        if 'user_role' not in st.session_state:
            st.session_state['user_role'] = 'guest'

        if "SESSION_SECRET_KEY" in os.environ:
            os.environ["STREAMLIT_SERVER_COOKIE_SECRET"] = os.getenv("SESSION_SECRET_KEY")
        elif not st.session_state.get('_secret_key_generated'):
            st.session_state['_secret_key_generated'] = secrets.token_hex(32)
            os.environ["STREAMLIT_SERVER_COOKIE_SECRET"] = st.session_state['_secret_key_generated']


    def login_user(self, email: str, role: str = 'free'):
        st.session_state['logged_in'] = True
        st.session_state['user_email'] = email
        st.session_state['user_role'] = role
        st.success(f"Welcome, {email}!")

    def logout_user(self):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = None
        st.session_state['user_role'] = 'guest'
        st.info("You have been logged out.")

    def is_logged_in(self) -> bool:
        return st.session_state.get('logged_in', False)

    def get_current_user_email(self) -> Optional[str]:
        return st.session_state.get('user_email')

    def get_current_user_role(self) -> str:
        return st.session_state.get('user_role', 'guest')

    def has_permission(self, feature_name: str) -> bool:
        current_role = self.get_current_user_role()
        return Permissions.check_permission(current_role, feature_name)
