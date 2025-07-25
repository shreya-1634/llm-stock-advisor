import streamlit as st
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

# -------------------- Streamlit Config --------------------
st.set_page_config(page_title="📈 LLM Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")

if "user" not in st.session_state:
    st.session_state.user = None

# -------------------- Sidebar Navigation --------------------
menu = st.sidebar.radio("🔧 Navigation", [
    "Login", "Register", "Verify Email", "Reset Password", "Dashboard", "Logout"
])

# -------------------- Sidebar Time Range --------------------
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
st.sidebar.subheader("📅 Select Time Range")
period_label = st.sidebar.selectbox("Choose a time range", list(local_yf_config.keys()), index=2)

# -------------------- Register Page --------------------
if menu == "Register":
    st.subheader("👤 Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        success, msg = register_user(username, email, password)
        st.success(msg) if success else st.error(msg)

# -------------------- Login Page --------------------
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
            st.error("Invalid credentials or unverified email.")

# -------------------- Email Verification --------------------
elif menu == "Verify Email":
    st.subheader("📨 Verify Email")
    email = st.text_input("Email")
    token = st.text_input("Verification Token")
    if st.button("Verify"):
        if verify_email(email, token):
            st.success("✅ Email verified!")
        else:
            st.error("❌ Invalid or expired token.")

# -------------------- Password Reset --------------------
elif menu == "Reset Password":
    st.subheader("🔑 Reset Password")
    stage = st.radio("Choose", ["Send Reset Token", "Reset with Token"])
    email = st.text_input("Email")

    if stage == "Send Reset Token":
        if st.button("Send Token"):
            initiate_password_reset(email)
            st.info("📧 Reset token sent to your email.")
    else:
        token = st.text_input("Reset Token")
        new_password = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if complete_password_reset(email, token, new_password):
                st.success("✅ Password reset successfully!")
            else:
                st.error("❌ Invalid or expired token.")

# -------------------- Dashboard --------------------
elif menu == "Dashboard":
    user = get_logged_in_user()
    if not user:
        st.warning("⚠️ Please login to access the dashboard.")
    else:
        st.success(f"Welcome, {user['username']}!")
        ticker = st.text_input("🔍 Enter Stock Ticker (e.g., AAPL, MSFT)")
        time_config = local_yf_config[period_label]
        if st.button("Fetch Data"):
            if ticker:
                df = fetch_stock_data(ticker, time_config["period"], time_config["interval"])
                if df is not None and not df.empty:
                    st.write("### 📊 Latest Stock Data")
                    st.dataframe(df.tail())

                    st.plotly_chart(create_interactive_chart(df), use_container_width=True)
                    st.plotly_chart(plot_rsi(df), use_container_width=True)
                    st.plotly_chart(plot_macd(df), use_container_width=True)
                else:
                    st.error("❌ No data found.")
            else:
                st.warning("⚠️ Please enter a ticker.")

# -------------------- Logout --------------------
elif menu == "Logout":
    logout_user()
    st.success("✅ Logged out successfully.")
