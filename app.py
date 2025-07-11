import streamlit as st
from core.auth import login_user, signup_user, get_logged_in_user, logout_user, initiate_password_reset, complete_password_reset
from core.data_fetcher import fetch_stock_data
from core.visualization import create_interactive_chart, plot_macd, plot_rsi

st.set_page_config(page_title="Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard", "Reset Password"])

# ---------------- Login ----------------
if menu == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success(f"Welcome back, {username}!")
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

# ---------------- Signup ----------------
elif menu == "Signup":
    st.subheader("📝 Create Account")
    username = st.text_input("New Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Signup"):
        if signup_user(username, email, password):
            st.success("Account created successfully!")
        else:
            st.error("Signup failed. Username may already exist.")

# ---------------- Password Reset ----------------
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
        st.warning("⚠️ Please login to access the dashboard.")
    else:
        st.success(f"Welcome {user['username']}!")
        
        if st.sidebar.button("Logout"):
            logout_user()
            st.info("Logged out successfully.")

        ticker = st.text_input("🔎 Enter Stock Ticker (e.g., AAPL, TSLA)")

        period_options = {
            "1 Day": "1d",
            "5 Days": "5d",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "Max": "max"
        }

        selected_period_label = st.selectbox("⏱️ Select Time Period", list(period_options.keys()), index=2)
        selected_period = period_options[selected_period_label]

        if ticker:
            st.info("📡 Fetching data...")
            df = fetch_stock_data(ticker, selected_period)

            if not df.empty:
                st.success("✅ Data fetched successfully!")
                st.plotly_chart(create_interactive_chart(df, ticker), use_container_width=True)

                with st.expander("📊 Technical Indicators"):
                    st.plotly_chart(plot_macd(df, ticker), use_container_width=True)
                    st.plotly_chart(plot_rsi(df, ticker), use_container_width=True)
            else:
                st.error("❌ No data available for the selected ticker and period.")
