import streamlit as st
from auths.auth import (
    authenticate_user,
    register_user,
    verify_email,
    initiate_password_reset,
    complete_password_reset,
    logout_user,
    get_logged_in_user
)
from core.visualization import (
    create_interactive_chart, 
    plot_rsi, 
    plot_macd
)
from core.data_fetcher import fetch_stock_data


# --------------------------
# Streamlit App Interface
# --------------------------
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 LLM Stock Advisor")

# --------------------------
# User Login/Register Logic
# --------------------------
menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Verify Email", "Reset Password", "Dashboard", "Logout"])

# --------------------------------------
# SESSION STATE: user
# --------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if menu == "Register":
    st.subheader("Create an Account")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        success, msg = register_user(username, email, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)

elif menu == "Verify Email":
    st.subheader("Verify Email")
    email = st.text_input("Registered Email")
    token = st.text_input("Verification Token")

    if st.button("Verify"):
        if verify_email(email, token):
            st.success("Email verified successfully!")
        else:
            st.error("Invalid or expired token.")

elif menu == "Reset Password":
    st.subheader("Reset Password")
    email = st.text_input("Registered Email")

    if st.button("Send Reset Token"):
        initiate_password_reset(email)
        st.info("Check your email for the reset token.")

    reset_token = st.text_input("Reset Token")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Reset Password"):
        if complete_password_reset(email, reset_token, new_pass):
            st.success("Password reset successfully!")
        else:
            st.error("Invalid or expired token.")

elif menu == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.session_state.user = user  # ✅ Store login state
            st.success(f"Welcome {user['username']}!")
        else:
            st.error("Invalid credentials or email not verified.")

elif menu == "Logout":
    logout_user()
    st.success("Logged out successfully.")

# --------------------------
# Dashboard after login
# --------------------------
elif menu == "Dashboard":
    user = get_logged_in_user()

    if user:
        st.subheader(f"Welcome, {user['username']}!")
        ticker = st.text_input("Enter stock ticker (e.g., AAPL, TSLA)")
        period = st.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"])

        if st.button("Fetch Data"):
            df = fetch_stock_data(ticker, period=period)
            if df is not None:
                st.plotly_chart(create_interactive_chart(df, ticker), use_container_width=True)
                st.plotly_chart(plot_rsi(df), use_container_width=True)
                st.plotly_chart(plot_macd(df), use_container_width=True)
            else:
                st.error("Failed to fetch data.")
    else:
        st.warning("Please login to fetch data of any ticker.")
