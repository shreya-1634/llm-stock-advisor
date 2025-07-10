import streamlit as st
from auths.auth import (
    register_user,
    authenticate_user,
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

st.set_page_config(page_title="Stock Advisor", layout="wide")

# ========== Session Handling ==========
user = get_logged_in_user()

# ========== Sidebar Navigation ==========
st.sidebar.title("🔐 Authentication")
menu = st.sidebar.radio("Navigate", ["Login", "Register", "Verify Email", "Reset Password", "Dashboard"])

# ========== Login ==========
if menu == "Login":
    st.title("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome back, {user['username']}!")
        else:
            st.error("Login failed. Make sure you're verified.")

# ========== Register ==========
elif menu == "Register":
    st.title("📝 Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        success, msg = register_user(username, email, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)

# ========== Verify Email ==========
elif menu == "Verify Email":
    st.title("📧 Verify Email")
    email = st.text_input("Email")
    token = st.text_input("Verification Token")
    if st.button("Verify"):
        if verify_email(email, token):
            st.success("Email verified successfully!")
        else:
            st.error("Verification failed or token expired.")

# ========== Reset Password ==========
elif menu == "Reset Password":
    st.title("🔁 Reset Password")
    sub_menu = st.radio("Step", ["Request Token", "Submit Token"])
    if sub_menu == "Request Token":
        email = st.text_input("Enter your email")
        if st.button("Send Reset Token"):
            initiate_password_reset(email)
            st.success("Reset token sent to your email.")
    else:
        email = st.text_input("Email")
        token = st.text_input("Reset Token")
        new_password = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if complete_password_reset(email, token, new_password):
                st.success("Password reset successful.")
            else:
                st.error("Invalid token or expired.")

# ========== Dashboard ==========
elif menu == "Dashboard":
    if not user:
        st.warning("Please log in to access the dashboard.")
    else:
        st.sidebar.success(f"Logged in as {user['username']}")
        if st.sidebar.button("Logout"):
            logout_user()
            st.experimental_rerun()

        st.title("📊 Stock Dashboard")

        ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL")
        if st.button("Fetch Data"):
            data = fetch_stock_data(ticker)
            if data is not None:
                st.plotly_chart(create_interactive_chart(data, ticker), use_container_width=True)
                st.plotly_chart(plot_rsi(data), use_container_width=True)
                st.plotly_chart(plot_macd(data), use_container_width=True)
            else:
                st.error("Failed to fetch data for given ticker.")
