import streamlit as st
from datetime import datetime
import json

from core.config import get_logger
from core.visualization import (
    create_interactive_chart,
    plot_rsi,
    plot_macd
)
from core.data_fetcher import fetch_stock_data
from core.predictor import predict_future_prices
from core.news_analyzer import news_analyzer, display_news_with_insights
from auths.auth import (
    authenticate_user,
    register_user,
    verify_email,
    initiate_password_reset,
    complete_password_reset,
    logout_user,
    get_logged_in_user
)

logger = get_logger(__name__)
email_conf = st.secrets["email"]
# ====================
# 🌐 Streamlit UI App
# ====================
def auth_interface():
    st.title("🔐 Login / Register")

    tabs = st.tabs(["Login", "Register", "Verify Email", "Reset Password"])

    # Login
    with tabs[0]:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.user = user
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials or unverified email.")

    # Register
    with tabs[1]:
        username = st.text_input("Username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            success, message = register_user(username, reg_email, reg_pass)
            if success:
                st.success(message)
            else:
                st.error(message)

    # Email Verification
    with tabs[2]:
        verify_email_input = st.text_input("Email to verify")
        token = st.text_input("Verification Token")
        if st.button("Verify Email"):
            if verify_email(verify_email_input, token):
                st.success("Email verified successfully.")
            else:
                st.error("Invalid or expired token.")

    # Password Reset
    with tabs[3]:
        reset_email = st.text_input("Email")
        if st.button("Send Reset Token"):
            initiate_password_reset(reset_email)
            st.info(f"Reset token sent to {reset_email}")

        reset_token = st.text_input("Enter Token")
        new_password = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if complete_password_reset(reset_email, reset_token, new_password):
                st.success("Password updated.")
            else:
                st.error("Token invalid or expired.")

# ====================
# 📊 Dashboard
# ====================
def dashboard():
    st.title("📊 Stock Dashboard")

    st.sidebar.title("📌 Navigation")
    selection = st.sidebar.radio("Go to", ["Market", "News", "Logout"])

    if selection == "Market":
        ticker = st.text_input("Enter Ticker Symbol", value="AAPL")
        if st.button("Fetch Stock Data"):
            data = fetch_stock_data(ticker, "2020-01-01", datetime.today().strftime('%Y-%m-%d'))
            if data is not None:
                st.plotly_chart(create_interactive_chart(data, ticker))
                st.subheader("📈 RSI")
                st.plotly_chart(plot_rsi(data))
                st.subheader("📉 MACD")
                st.plotly_chart(plot_macd(data))
                st.subheader("📊 LSTM Prediction")
                forecast = predict_future_prices(data)
                st.line_chart(forecast)

    elif selection == "News":
        news = news_analyzer("AAPL")
        display_news_with_insights(news)

    elif selection == "Logout":
        logout_user()
        st.success("Logged out successfully.")
        st.experimental_rerun()

# ====================
# 🚀 Main Entry
# ====================
def main():
    st.set_page_config(page_title="LLM Stock Advisor", layout="wide")
    if get_logged_in_user():
        dashboard()
    else:
        auth_interface()

if __name__ == "__main__":
    main()
