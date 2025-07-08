#!/usr/bin/env python3
"""
Stock Advisor Pro - Complete Authentication System
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Fix imports and paths
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from auth.auth import (
        initialize_db,
        register_user,
        authenticate_user,
        verify_email,
        initiate_password_reset,
        complete_password_reset
    )
    from core.config import setup_logging, get_logger
    from core.data_fetcher import fetch_stock_data
    from core.visualization import create_interactive_chart
except ImportError as e:
    st.error(f"Module import error: {str(e)}")
    st.error("Please install required packages:")
    st.code("""
    pip install -r requirements.txt
    # Or manually:
    pip install streamlit bcrypt psycopg2-binary python-dotenv pandas yfinance plotly
    """)
    st.stop()

# Initialize system
setup_logging()
logger = get_logger(__name__)
initialize_db()

# Page configuration
st.set_page_config(
    page_title="Stock Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
        .main { padding-top: 2rem; }
        .stTextInput input { font-size: 16px; }
        .stButton button { width: 100%; }
        .error { color: #ff4b4b; }
        .success { color: #09ab3b; }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #4b6cb7 0%, #182848 100%);
        }
        .sidebar .sidebar-content {
            background: transparent;
        }
    </style>
    """, unsafe_allow_html=True)

def handle_email_verification(token):
    """Process email verification token"""
    success, message = verify_email(token)
    if success:
        st.session_state.verification_status = (True, message)
    else:
        st.session_state.verification_status = (False, message)
    st.experimental_set_query_params()

def handle_password_reset(token):
    """Handle password reset flow"""
    st.title("🔑 Reset Your Password")
    new_password = st.text_input("New Password", type="password", key="reset_pw")
    confirm_password = st.text_input("Confirm Password", type="password", key="reset_pw_confirm")
    
    if st.button("Update Password"):
        if new_password != confirm_password:
            st.error("Passwords don't match!")
        elif len(new_password) < 8:
            st.error("Password must be at least 8 characters")
        else:
            if complete_password_reset(token, new_password):
                st.success("Password updated successfully! Please login.")
                st.experimental_set_query_params()
            else:
                st.error("Invalid or expired reset link")

def show_auth_interface():
    """Show login/registration interface"""
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "🔑 Forgot Password"])
    
    with tab1:
        st.header("Login to Your Account")
        identifier = st.text_input("Email or Username", key="login_id")
        password = st.text_input("Password", type="password", key="login_pw")
        
        if st.button("Sign In", type="primary"):
            user_id = authenticate_user(identifier, password)
            if user_id:
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("Invalid credentials or email not verified")

    with tab2:
        st.header("Create New Account")
        email = st.text_input("Email Address", key="reg_email")
        username = st.text_input("Username", key="reg_user")
        full_name = st.text_input("Full Name", key="reg_name")
        password = st.text_input("Password", type="password", key="reg_pw")
        confirm = st.text_input("Confirm Password", type="password", key="reg_pw2")
        
        if st.button("Register", type="primary"):
            if password != confirm:
                st.error("Passwords don't match!")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                success, message = register_user(email, username, password, full_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with tab3:
        st.header("Reset Your Password")
        email = st.text_input("Registered Email", key="reset_email")
        if st.button("Send Reset Link", type="primary"):
            if initiate_password_reset(email):
                st.success("Reset link sent to your email!")
            else:
                st.error("Failed to send reset link")

def show_main_app():
    """Main application after login"""
    st.title("📈 Stock Advisor Pro")
    
    # Stock analysis UI
    st.sidebar.header("Analysis Parameters")
    ticker = st.sidebar.text_input("Ticker Symbol", "AAPL").upper()
    days = st.sidebar.slider("Analysis Period (days)", 30, 365, 90)
    
    if st.sidebar.button("Analyze", type="primary"):
        with st.spinner("Crunching market data..."):
            try:
                data = fetch_stock_data(ticker, datetime.now() - timedelta(days=days), datetime.now())
                st.plotly_chart(create_interactive_chart(data), use_container_width=True)
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

def main():
    load_css()
    
    # Check for verification/reset tokens in URL
    params = st.experimental_get_query_params()
    if "verify" in params:
        handle_email_verification(params["verify"][0])
    elif "reset" in params:
        handle_password_reset(params["reset"][0])
    elif "user_id" not in st.session_state:
        show_auth_interface()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
