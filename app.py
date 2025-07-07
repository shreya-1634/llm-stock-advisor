import streamlit as st
from auth.auth import authenticate_user, logout_user
from core.data_fetcher import fetch_stock_data
from core.visualization import create_interactive_chart, plot_volatility
from core.news_analyzer import fetch_news, display_news
from core.predictor import predict_future_prices
from core.trading_engine import TradingEngine
from auth.permissions import check_permission, request_permission
import datetime

# Page configuration
st.set_page_config(
    page_title="AI Stock Advisor",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'trading_engine' not in st.session_state:
    st.session_state.trading_engine = None

# Authentication flow
def login_section():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.trading_engine = TradingEngine(username)
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")

def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()
    
    st.title("AI Stock Advisor 🤖📈")
    
    # Stock selection
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")
    start_date = st.date_input("Start Date", datetime.date(2020, 1, 1))
    end_date = st.date_input("End Date", datetime.date.today())
    
    if st.button("Analyze"):
        with st.spinner("Fetching data and analyzing..."):
            # Fetch and display stock data
            stock_data = fetch_stock_data(ticker, start_date, end_date)
            st.plotly_chart(create_interactive_chart(stock_data), use_container_width=True)
            
            # Volatility display
            st.subheader("Market Volatility")
            plot_volatility(stock_data)
            
            # News analysis
            st.subheader("Relevant News")
            news = fetch_news(ticker)
            display_news(news)
            
            # AI predictions
            st.subheader("AI Price Predictions")
            future_days = st.slider("Prediction days", 1, 30, 7)
            prediction = predict_future_prices(stock_data, future_days)
            st.plotly_chart(create_interactive_chart(prediction), use_container_width=True)
            
            # Trading recommendation
            st.subheader("Trading Recommendation")
            recommendation = st.session_state.trading_engine.generate_recommendation(stock_data, news)
            st.write(f"AI Suggestion: **{recommendation}**")
            
            if recommendation != "HOLD":
                permission_key = request_permission(
                    st.session_state.username,
                    recommendation,
                    ticker,
                    1  # Default to 1 share for demo
                )
                if st.button(f"Allow {recommendation} for {ticker}"):
                    if check_permission(permission_key):
                        st.success(f"Trade executed: {recommendation} 1 share of {ticker}")
                    else:
                        st.error("Permission denied or expired")

# Render appropriate view
if not st.session_state.authenticated:
    login_section()
else:
    main_app()
