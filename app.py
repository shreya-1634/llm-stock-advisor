import streamlit as st
from auths.auth import (
    register_user, authenticate_user, verify_email,
    initiate_password_reset, complete_password_reset,
    get_user_info, init_db
)
from core.news_analyzer import news_analyzer, display_news_with_insights
from core.data_fetcher import fetch_stock_data
from core.predictor import predict_future_prices
from core.visualization import create_interactive_chart, plot_volatility
from core.trading_engine import TradingEngine
from datetime import datetime

# Initialize user DB on startup
init_db()

# Page setup
st.set_page_config(page_title="📊 Stock Advisor", layout="wide")
st.title("📈 LLM-Powered Stock Advisor")

# --- EMAIL VERIFICATION HANDLING ---
query_params = st.experimental_get_query_params()
if "verify_token" in query_params:
    token = query_params["verify_token"][0]
    if verify_email(token):
        st.success("✅ Email verified successfully! You can now login.")
    else:
        st.error("❌ Invalid or expired verification link.")

# --- PASSWORD RESET HANDLING ---
if "reset_token" in query_params:
    token = query_params["reset_token"][0]
    st.subheader("🔐 Reset Password")
    new_pw = st.text_input("Enter New Password", type="password")
    if st.button("Reset Password"):
        if complete_password_reset(token, new_pw):
            st.success("✅ Password reset successfully. You may now login.")
        else:
            st.error("❌ Invalid or expired token.")
    st.stop()

# --- SESSION STATE HANDLING ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN / REGISTER UI ---
if not st.session_state["authenticated"]:
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "🔁 Reset Password"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(email, pw):
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = email
                name, is_admin = get_user_info(email)
                st.session_state["user_name"] = name
                st.session_state["is_admin"] = bool(is_admin)
                st.experimental_rerun()
            else:
                st.error("Login failed or email not verified.")

    with tab2:
        st.subheader("Register")
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="register_email")
        pw = st.text_input("Password", type="password", key="register_pw")
        if st.button("Register"):
            if register_user(name, email, pw):
                st.success("✅ Registered successfully! Check your email to verify.")
            else:
                st.error("❌ Email already registered.")

    with tab3:
        st.subheader("Reset Password")
        email = st.text_input("Enter your email", key="reset_email")
        if st.button("Send Reset Link"):
            initiate_password_reset(email)
            st.info("📧 If your email exists, a reset link has been sent.")
    st.stop()

# --- LOGGED IN UI ---
st.sidebar.success(f"👋 Welcome, {st.session_state['user_name']}")
if st.sidebar.button("Logout"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun()

if st.session_state["is_admin"]:
    st.sidebar.markdown("🛠 **Admin Access Enabled**")

# --- APP FUNCTIONALITY ---
st.markdown("### 🔍 Search a Stock")
ticker = st.text_input("Enter stock ticker symbol (e.g., AAPL)", value="AAPL")

if ticker:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Fetching historical stock data...")
        data = fetch_stock_data(ticker)
        st.plotly_chart(create_interactive_chart(data), use_container_width=True)
        st.plotly_chart(plot_volatility(data), use_container_width=True)

    with col2:
        st.info("Predicting future prices...")
        predicted_df = predict_future_prices(data)
        st.dataframe(predicted_df)

    st.markdown("---")
    st.subheader("📰 Latest Financial News & AI Insights")
    news = news_analyzer.fetch_financial_news(ticker)
    display_news_with_insights(news)

    st.markdown("---")
    st.subheader("📊 Recommendation Engine")
    trader = TradingEngine(username=st.session_state["user_email"])
    recommendation = trader.generate_recommendation(data, news)
    st.metric("📌 Recommendation", recommendation)
