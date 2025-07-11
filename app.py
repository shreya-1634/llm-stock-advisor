import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

from core.visualization import create_interactive_chart, plot_rsi, plot_macd
from core.data_fetcher import fetch_stock_data
from auths.auth import (
    register_user,
    authenticate_user,
    verify_email,
    initiate_password_reset,
    complete_password_reset,
    logout_user,
    get_logged_in_user,
)

# App configuration
st.set_page_config(page_title="📈 LLM Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")

if "user" not in st.session_state:
    st.session_state.user = None

menu = st.sidebar.radio("🔧 Navigation", ["Login", "Register", "Verify Email", "Reset Password", "Dashboard", "Logout"])

# ✅ Google Finance-style time ranges
local_yf_config = {
    "1 Day": {"period": "1d", "interval": "5m"},
    "5 Days": {"period": "5d", "interval": "15m"},
    "1 Month": {"period": "1mo", "interval": "30m"},
    "3 Months": {"period": "3mo", "interval": "1h"},
    "6 Months": {"period": "6mo", "interval": "1d"},
    "1 Year": {"period": "1y", "interval": "1d"},
    "5 Years": {"period": "5y", "interval": "1wk"},
    "Max": {"period": "max", "interval": "1mo"}
}

# Time period selector
st.sidebar.subheader("📅 Select Time Range")
period_label = st.sidebar.selectbox(
    "Choose a time range",
    options=list(local_yf_config.keys()),
    index=2  # Default: "1 Month"
)

# ---------------- Register ----------------
if menu == "Register":
    st.subheader("👤 Register New User")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        success, msg = register_user(username, email, password)
        st.success(msg) if success else st.error(msg)

# ---------------- Login ----------------
elif menu == "Login":
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome {user['username']}!")
        else:
            st.error("Invalid credentials or email not verified.")

# ---------------- Verify Email ----------------
elif menu == "Verify Email":
    st.subheader("📨 Email Verification")
    email = st.text_input("Registered Email")
    token = st.text_input("Verification Token")
    if st.button("Verify"):
        if verify_email(email, token):
            st.success("✅ Email verified successfully!")
        else:
            st.error("❌ Invalid or expired token.")

# ---------------- Reset Password ----------------
elif menu == "Reset Password":
    st.subheader("🔑 Password Reset")
    stage = st.radio("Stage", ["Send Reset Token", "Reset with Token"])
    email = st.text_input("Email")
    if stage == "Send Reset Token":
        if st.button("Send Reset Email"):
            initiate_password_reset(email)
            st.info("Reset token sent to your email.")
    else:
        token = st.text_input("Reset Token")
        new_password = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if complete_password_reset(email, token, new_password):
                st.success("Password reset successful.")
            else:
                st.error("Invalid or expired reset token.")

# ---------------- Dashboard ----------------
elif menu == "Dashboard":
    user = get_logged_in_user()
    if not user:
        st.warning("⚠️ Please login to fetch data of any ticker.")
    else:
        st.success(f"Welcome {user['username']}!")

        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)")

        if st.button("Fetch Data") and ticker:
            config = local_yf_config.get(period_label, {"period": "1mo", "interval": "1d"})
            period = config["period"]
            interval = config["interval"]

            st.info(f"📡 Fetching {period_label} data for {ticker}...")

            df = fetch_stock_data(ticker, period=period, interval=interval)

            if not df.empty:
                   st.plotly_chart(create_interactive_chart(df, ticker), use_container_width=True)
                st.plotly_chart(plot_macd(df), use_container_width=True)
            st.plotly_chart(plot_rsi(df), use_container_width=True)
            else:
                st.warning("❌ No data available for the selected ticker and period.")

# ---------------- Logout ----------------
elif menu == "Logout":
    logout_user()
    st.success("✅ Logged out successfully.")
