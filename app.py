#!/usr/bin/env python3
"""
Stock Advisor Pro - Complete Application
"""

import time
import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

from auths.auth import (
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
from core.predictor import predict_future_prices
from core.news_analyzer import news_analyzer, display_news_with_insights
from core.trading_engine import TradingEngine
import plotly.graph_objects as go

# Add root path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
setup_logging()
logger = get_logger(__name__)

# App title and settings
st.set_page_config(page_title="📊 LLM Stock Advisor Pro", layout="wide")
st.markdown("<h1 style='text-align: center;'>📊 LLM Stock Advisor Pro</h1>", unsafe_allow_html=True)
st.markdown("---")

# Initialize DB
try:
    if not initialize_db():
        st.error("⚠️ Failed to initialize database")
        st.stop()
except Exception as e:
    st.exception(f"Database Initialization Failed: {e}")
    st.stop()

# Authentication Block
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

auth_tab = st.sidebar.radio("👤 Authentication", ["Login", "Register", "Reset Password"])
if not st.session_state.authenticated:
    if auth_tab == "Login":
        st.sidebar.subheader("🔐 Login")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user_id = authenticate_user(email, password)
            if user_id:
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.success("✅ Logged in successfully")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials")

    elif auth_tab == "Register":
        st.sidebar.subheader("📝 Register")
        name = st.sidebar.text_input("Name")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        confirm = st.sidebar.text_input("Confirm Password", type="password")
        if st.sidebar.button("Register"):
            if password == confirm:
                registered = register_user(name, email, password)
                if registered:
                    st.success("✅ Registered! Please log in.")
                else:
                    st.error("Registration failed.")
            else:
                st.warning("Passwords do not match")

    elif auth_tab == "Reset Password":
        st.sidebar.subheader("🔁 Reset Password")
        email = st.sidebar.text_input("Email")
        new_pass = st.sidebar.text_input("New Password", type="password")
        otp = st.sidebar.text_input("Enter OTP")
        if st.sidebar.button("Request OTP"):
            initiate_password_reset(email)
            st.info("OTP sent if email exists.")
        if st.sidebar.button("Reset"):
            if complete_password_reset(email, otp, new_pass):
                st.success("✅ Password reset successful.")
            else:
                st.error("❌ OTP or Email invalid")

# MAIN APP
if st.session_state.authenticated:

    st.sidebar.success(f"👋 Welcome, {st.session_state.user_id}")
    ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")
    hist_days = st.sidebar.slider("📅 History (days)", 30, 1500, 365)
    pred_days = st.sidebar.slider("🔮 Predict Days", 1, 15, 7)
    show_news = st.sidebar.checkbox("🗞️ Show News", value=True)

    if not ticker:
        st.warning("Enter a valid ticker to proceed.")
        st.stop()

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=hist_days)

        # Data fetching
        data = fetch_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        st.subheader(f"📊 Historical Chart - {ticker}")
        st.plotly_chart(create_interactive_chart(data), use_container_width=True)

        # Forecasting
        st.subheader("📈 LSTM Forecast")
        future_df = predict_future_prices(data, pred_days)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Historical"))
        fig.add_trace(go.Scatter(x=future_df.index, y=future_df["Close"], name="Forecasted"))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # News & Sentiment
        if show_news:
            st.subheader("📰 News & Sentiment")
            news = news_analyzer.fetch_financial_news(ticker)
            display_news_with_insights(news)
        else:
            news = None

        # Smart Trade Suggestion
        st.subheader("🧠 Smart Trade Recommendation")
        engine = TradingEngine(username=st.session_state.user_id)
        result = engine.generate_recommendation(data, news)
        st.info(f"💡 **Recommendation:** `{result['recommendation']}`")

        st.markdown("### 📊 Signal Strengths")
        col1, col2, col3 = st.columns(3)
        col1.metric("📉 MA Signal", result['indicators']['MA Signal'])
        col2.metric("📈 RSI Signal", result['indicators']['RSI Signal'])
        col3.metric("💬 Sentiment", result['indicators']['Sentiment Signal'])

        # Export Option
        st.download_button(
            label="📥 Export Chart as Image",
            data=fig.to_image(format="png"),
            file_name=f"{ticker}_forecast.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"Error: {e}")
