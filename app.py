import streamlit as st
import pandas as pd  
import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta

from core.config import get_logger
from core.visualization import create_interactive_chart, plot_rsi, plot_macd
from core.data_fetcher import fetch_stock_data, yf_config
from auths.auth import (
    register_user,
    authenticate_user,
    verify_email,
    initiate_password_reset,
    complete_password_reset,
    logout_user,
    get_logged_in_user,
)

logger = get_logger(__name__)
DB_FILE = "users.db"

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="LLM Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")

# --------------------------
# Session Initialization
# --------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# --------------------------
# Sidebar Navigation
# --------------------------
menu = st.sidebar.radio("🔧 Navigation", ["Login", "Register", "Verify Email", "Reset Password", "Dashboard", "Logout"])

# --------------------------
# Period Selector (Global)
# --------------------------
st.sidebar.subheader("📅 Select Time Period")
period = st.sidebar.selectbox(
    "Choose a time range",
    options=["7d", "30d", "90d", "180d", "365d"],
    index=1,
    format_func=lambda x: {
        "7d": "Last 7 Days",
        "30d": "Last 30 Days",
        "90d": "Last 3 Months",
        "180d": "Last 6 Months",
        "365d": "Last 1 Year"
    }[x]
)

# --------------------------
# Register
# --------------------------
if menu == "Register":
    st.subheader("👤 Register New User")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        success, msg = register_user(username, email, password)
        st.success(msg) if success else st.error(msg)

# --------------------------
# Login
# --------------------------
elif menu == "Login":
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.session_state.user = user
            st.success(f"✅ Welcome {user['username']}!")
        else:
            st.error("❌ Invalid credentials or email not verified.")

# --------------------------
# Email Verification
# --------------------------
elif menu == "Verify Email":
    st.subheader("📨 Email Verification")
    email = st.text_input("Registered Email")
    token = st.text_input("Verification Token")
    if st.button("Verify"):
        if verify_email(email, token):
            st.success("✅ Email verified successfully!")
        else:
            st.error("❌ Invalid or expired token.")

# --------------------------
# Password Reset
# --------------------------
elif menu == "Reset Password":
    st.subheader("🔑 Password Reset")
    stage = st.radio("Stage", ["Send Reset Token", "Reset with Token"])
    email = st.text_input("Email")
    if stage == "Send Reset Token":
        if st.button("Send Reset Email"):
            initiate_password_reset(email)
            st.info("📨 Reset token sent to your email.")
    else:
        token = st.text_input("Reset Token")
        new_password = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if complete_password_reset(email, token, new_password):
                st.success("✅ Password reset successful.")
            else:
                st.error("❌ Invalid or expired reset token.")

# --------------------------
# Dashboard
# --------------------------
elif menu == "Dashboard":
    user = get_logged_in_user()
    if not user:
        st.warning("⚠️ Please login to fetch data of any ticker.")
    else:
        st.success(f"Welcome {user['username']}!")

        # 📅 Time Range selector like Google Finance
        from core.data_fetcher import fetch_stock_data, yf_config

        period_label = st.sidebar.selectbox(
            "📅 Choose a time range",
            options=list(yf_config.keys()),
            index=3,  # Default to "1 Month"
            format_func=lambda x: x  # You can format labels if needed
        )

        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)")

        if st.button("Fetch Data") and ticker:
            st.info("📡 Fetching data...")
            df = fetch_stock_data(ticker, label=period_label)

            if not df.empty:
                st.subheader(f"📊 Price Chart for {ticker.upper()} ({period_label})")
                st.plotly_chart(create_interactive_chart(df, ticker), use_container_width=True)

                st.subheader("📉 RSI Indicator")
                st.plotly_chart(plot_rsi(df), use_container_width=True)

                st.subheader("📈 MACD Indicator")
                st.plotly_chart(plot_macd(df), use_container_width=True)
            else:
                st.warning("❌ No data available for the selected ticker and period.")


# --------------------------
# Logout
# --------------------------
elif menu == "Logout":
    logout_user()
    st.success("✅ Logged out successfully.")
