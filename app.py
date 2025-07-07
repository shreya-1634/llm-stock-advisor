import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from auth.auth import authenticate_user, logout_user
from core.data_fetcher import fetch_stock_data, get_current_price
from core.visualization import create_interactive_chart, plot_volatility
from core.news_analyzer import fetch_financial_news, display_news_with_insights
from core.predictor import predict_future_prices
from core.trading_engine import TradingEngine
from auth.permissions import request_permission, check_permission
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="AI Stock Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State Management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'trading_engine' not in st.session_state:
    st.session_state.trading_engine = None
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = "AAPL"

# Authentication Functions
def login_section():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login", key="login_btn"):
        if authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.trading_engine = TradingEngine(username)
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")

def logout_section():
    if st.sidebar.button("Logout", key="logout_btn"):
        logout_user()
        st.rerun()

# Main Application
def main_app():
    st.sidebar.title(f"👋 Welcome, {st.session_state.username}")
    logout_section()
    
    # Stock Selection Panel
    st.sidebar.header("Stock Selection")
    st.session_state.current_ticker = st.sidebar.text_input(
        "Ticker Symbol", 
        value=st.session_state.current_ticker
    ).upper()
    
    date_range = st.sidebar.selectbox(
        "Date Range",
        ["1M", "3M", "6M", "YTD", "1Y", "5Y", "Max"],
        index=2
    )
    
    # Convert date range to start date
    date_map = {
        "1M": datetime.now() - timedelta(days=30),
        "3M": datetime.now() - timedelta(days=90),
        "6M": datetime.now() - timedelta(days=180),
        "YTD": datetime(datetime.now().year, 1, 1),
        "1Y": datetime.now() - timedelta(days=365),
        "5Y": datetime.now() - timedelta(days=5*365),
        "Max": datetime(1980, 1, 1)
    }
    
    # Main Dashboard
    st.title(f"AI Stock Advisor: {st.session_state.current_ticker}")
    
    if st.sidebar.button("Analyze", type="primary"):
        with st.spinner("🧠 Processing data with AI..."):
            try:
                # Fetch and display data
                stock_data = fetch_stock_data(
                    st.session_state.current_ticker,
                    date_map[date_range],
                    datetime.now()
                )
                
                # Visualization
                col1, col2 = st.columns([7, 3])
                with col1:
                    st.plotly_chart(
                        create_interactive_chart(stock_data),
                        use_container_width=True
                    )
                with col2:
                    st.metric(
                        "Current Price", 
                        f"${get_current_price(st.session_state.current_ticker):.2f}"
                    )
                    plot_volatility(stock_data)
                
                # News Analysis
                st.header("📰 AI-Processed News")
                news = fetch_financial_news(st.session_state.current_ticker)
                display_news_with_insights(news)
                
                # AI Predictions
                st.header("🔮 AI Price Prediction")
                prediction_days = st.slider(
                    "Prediction Period (days)", 
                    1, 30, 7, key="pred_days"
                )
                predictions = predict_future_prices(stock_data, prediction_days)
                st.plotly_chart(
                    create_interactive_chart(predictions),
                    use_container_width=True
                )
                
                # Trading Recommendation
                st.header("🤖 Trading Advice")
                recommendation = st.session_state.trading_engine.generate_recommendation(
                    stock_data, 
                    news
                )
                
                st.success(f"**AI Recommendation:** {recommendation}")
                
                if recommendation != "HOLD":
                    permission_key = request_permission(
                        st.session_state.username,
                        recommendation,
                        st.session_state.current_ticker,
                        1  # Default to 1 share
                    )
                    
                    if st.button(f"Approve {recommendation} Order"):
                        if check_permission(permission_key):
                            st.session_state.trading_engine.execute_trade(
                                recommendation,
                                st.session_state.current_ticker,
                                1
                            )
                            st.toast(f"Trade executed: {recommendation} {st.session_state.current_ticker}")
                        else:
                            st.error("Permission denied or expired")
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

# Render the appropriate view
if not st.session_state.authenticated:
    login_section()
    st.markdown("""
    ## Welcome to AI Stock Advisor
    Please login to access:
    - 📈 Real-time stock analysis
    - 📰 AI-processed financial news
    - 🔮 Predictive market insights
    - 🤖 Automated trading recommendations
    """)
else:
    main_app()
