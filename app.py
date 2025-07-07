#!/usr/bin/env python3
"""
AI Stock Advisor Pro - Production Version
"""

import sys
import os
from pathlib import Path
import traceback
from datetime import datetime, timedelta
import streamlit as st

# ==================== PATH CONFIGURATION ====================
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# ==================== MODULE IMPORTS ====================
try:
    from core.config import setup_logging, get_logger
    from auth.auth import authenticate_user, logout_user, check_permission
    from core.data_fetcher import fetch_stock_data, get_current_price
    from core.visualization import create_interactive_chart, plot_volatility
    from core.news_analyzer import news_analyzer, display_news_with_insights
    from core.predictor import predict_future_prices
    from core.trading_engine import TradingEngine
except ImportError as e:
    st.error(f"System Error: Failed to load modules. Contact support.\nError: {str(e)}")
    st.stop()

# Initialize system
setup_logging()
logger = get_logger(__name__)

# ==================== STREAMLIT CONFIG ====================
st.set_page_config(
    page_title="AI Stock Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
def load_css():
    css_path = PROJECT_ROOT / "static" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==================== SESSION MANAGEMENT ====================
def init_session():
    required_keys = {
        'authenticated': False,
        'username': None,
        'trading_engine': None,
        'current_ticker': "AAPL"
    }
    for key, val in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ==================== AUTHENTICATION ====================
def login_section():
    with st.sidebar:
        st.title("🔐 Authentication")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="login_btn"):
            if authenticate_user(username, password):
                st.session_state.update({
                    'authenticated': True,
                    'username': username,
                    'trading_engine': TradingEngine(username)
                })
                st.rerun()
            else:
                st.error("Invalid credentials")

def logout_section():
    if st.sidebar.button("Logout"):
        logout_user()
        st.session_state.clear()
        st.rerun()

# ==================== STOCK ANALYSIS ====================
def stock_analysis_section():
    # User greeting
    st.sidebar.title(f"👋 {st.session_state.username}")
    logout_section()
    
    # Stock controls
    with st.sidebar:
        st.header("📊 Analysis Parameters")
        ticker = st.text_input(
            "Ticker Symbol", 
            value=st.session_state.current_ticker
        ).upper()
        
        date_range = st.selectbox(
            "Timeframe",
            ["1M", "3M", "6M", "YTD", "1Y", "5Y"],
            index=2
        )
        
        date_map = {
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "6M": timedelta(days=180),
            "YTD": datetime(datetime.now().year, 1, 1),
            "1Y": timedelta(days=365),
            "5Y": timedelta(days=5*365)
        }

        if st.button("Analyze", type="primary"):
            st.session_state.current_ticker = ticker
            start_date = datetime.now() - date_map[date_range] if isinstance(date_map[date_range], timedelta) else date_map[date_range]
            analyze_stock(ticker, start_date)

def analyze_stock(ticker: str, start_date: datetime):
    with st.spinner("🔍 Analyzing market data..."):
        try:
            # Data processing
            stock_data = fetch_stock_data(ticker, start_date, datetime.now())
            current_price = get_current_price(ticker)
            news = news_analyzer.fetch_financial_news(ticker)
            
            # Display results
            col1, col2 = st.columns([7, 3])
            with col1:
                st.plotly_chart(
                    create_interactive_chart(stock_data),
                    use_container_width=True
                )
            with col2:
                st.metric("Current Price", f"${current_price:.2f}")
                plot_volatility(stock_data)
            
            # News and predictions
            st.header("📰 Market Insights")
            display_news_with_insights(news)
            
            st.header("🔮 AI Forecast")
            predictions = predict_future_prices(stock_data, 7)
            st.plotly_chart(
                create_interactive_chart(predictions),
                use_container_width=True
            )
            
            # Trading signals
            if check_permission(st.session_state.username, "trade"):
                st.header("💡 Trading Signal")
                recommendation = st.session_state.trading_engine.generate_recommendation(stock_data, news)
                st.success(f"Recommendation: {recommendation}")

        except Exception as e:
            logger.error(f"Analysis error: {traceback.format_exc()}")
            st.error("Analysis failed. Please try again.")

# ==================== MAIN APP ====================
def main():
    load_css()
    init_session()
    
    if not st.session_state.authenticated:
        login_section()
        st.info("Please login to access the AI Stock Advisor")
    else:
        stock_analysis_section()

if __name__ == "__main__":
    main()
