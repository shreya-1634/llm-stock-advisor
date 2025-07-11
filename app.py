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
        st.warning("⚠️ Please login to fetch data.")
    else:
        st.success(f"Welcome {user['username']}!")

        # --- Ticker and Source ---
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)")
        period = st.selectbox("📅 Select Time Range", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)
        interval = st.selectbox("⏰ Interval", ["1m", "5m", "15m", "1h", "1d"], index=4)

        if st.button("📡 Fetch Data") and ticker:
            st.info("Fetching stock data...")

            from core.data_fetcher import fetch_stock_data
            df = fetch_stock_data(ticker, period=period, interval=interval)

            if not df.empty:
                st.subheader("📊 Price Chart")
                st.plotly_chart(create_interactive_chart(df, ticker))
                st.subheader("📈 RSI Indicator")
                st.plotly_chart(plot_rsi(df))
                st.subheader("📉 MACD Indicator")
                st.plotly_chart(plot_macd(df))

                # --- News and Insights ---
                from core.news_analyzer import news_analyzer, display_news_with_insights
                st.subheader("📰 Latest Financial News")
                news = news_analyzer.fetch_financial_news(ticker)
                display_news_with_insights(news)

                # --- Recommendation ---
                from core.trading_engine import TradingEngine
                st.subheader("🤖 AI Recommendation")
                engine = TradingEngine(user["username"])
                recommendation = engine.generate_recommendation(df, news)
                st.write(f"### {recommendation}")

            else:
                st.warning("❌ No data available for this ticker and selected time period.")

# ---------------- Logout ----------------
elif menu == "Logout":
    logout_user()
    st.success("✅ Logged out successfully.")
