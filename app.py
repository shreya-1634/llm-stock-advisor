#!/usr/bin/env python3
"""
AI Stock Advisor Pro - Final Production Version
"""

import sys
import os
from pathlib import Path
import traceback
from datetime import datetime, timedelta
import streamlit as st

# ========================================================
# SECTION 1: CRITICAL PATH FIXES (SOLVES IMPORT ERRORS)
# ========================================================

# Get absolute path to project root (works in all environments)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add to Python path (permanent fix for imports)
sys.path.insert(0, str(PROJECT_ROOT))

# Now import all project modules AFTER path is fixed
try:
    from core.config import setup_logging, get_logger
    from auth.auth import authenticate_user, logout_user
    from core.data_fetcher import fetch_stock_data, get_current_price
    from core.visualization import create_interactive_chart, plot_volatility
    from core.news_analyzer import news_analyzer, display_news_with_insights
    from core.predictor import predict_future_prices
    from core.trading_engine import TradingEngine
    from auth.permissions import request_permission, check_permission
except ImportError as e:
    st.error(f"CRITICAL: Failed to import required modules. Error: {str(e)}")
    st.stop()

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# ========================================================
# SECTION 2: STREAMLIT APP CONFIGURATION
# ========================================================

st.set_page_config(
    page_title="AI Stock Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    """Load custom CSS styles"""
    css_path = PROJECT_ROOT / "static" / "styles.css"
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"CSS not loaded: {str(e)}")

def init_session():
    """Initialize session state variables"""
    defaults = {
        'authenticated': False,
        'trading_engine': None,
        'current_ticker': "AAPL",
        'username': None
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ========================================================
# SECTION 3: AUTHENTICATION COMPONENTS
# ========================================================

def login_section():
    """Render login form and handle authentication"""
    with st.sidebar:
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            try:
                if authenticate_user(username, password):
                    st.session_state.update({
                        'authenticated': True,
                        'username': username,
                        'trading_engine': TradingEngine(username)
                    })
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                logger.error(f"Login error: {traceback.format_exc()}")
                st.error("Authentication service unavailable")

def logout_section():
    """Handle user logout"""
    if st.sidebar.button("Logout"):
        try:
            logout_user()
            st.session_state.clear()
            st.rerun()
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            st.error("Logout failed")

# ========================================================
# SECTION 4: CORE STOCK ANALYSIS FUNCTIONALITY
# ========================================================

def stock_analysis_section():
    """Main stock analysis dashboard"""
    st.sidebar.title(f"👋 Welcome, {st.session_state.username}")
    logout_section()
    
    # Stock selection controls
    with st.sidebar:
        st.header("Stock Selection")
        ticker = st.text_input(
            "Ticker Symbol", 
            value=st.session_state.current_ticker
        ).upper()
        
        date_range = st.selectbox(
            "Date Range",
            ["1M", "3M", "6M", "YTD", "1Y", "5Y", "Max"],
            index=2
        )
        
        date_map = {
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "6M": timedelta(days=180),
            "YTD": datetime(datetime.now().year, 1, 1),
            "1Y": timedelta(days=365),
            "5Y": timedelta(days=5*365),
            "Max": datetime(1980, 1, 1)
        }

        if st.button("Analyze", type="primary"):
            st.session_state.current_ticker = ticker
            start_date = datetime.now() - date_map[date_range] if isinstance(date_map[date_range], timedelta) else date_map[date_range]
            analyze_stock(ticker, start_date)

def analyze_stock(ticker, start_date):
    """Core analysis pipeline for a given stock"""
    with st.spinner("🧠 Processing data with AI..."):
        try:
            # Data fetching
            stock_data = fetch_stock_data(ticker, start_date, datetime.now())
            if stock_data.empty:
                st.error("No data available for this ticker")
                return

            # Layout
            col1, col2 = st.columns([7, 3])
            
            # Main chart
            with col1:
                st.plotly_chart(
                    create_interactive_chart(stock_data),
                    use_container_width=True
                )
            
            # Side metrics
            with col2:
                try:
                    current_price = get_current_price(ticker)
                    st.metric("Current Price", f"${current_price:.2f}")
                except Exception:
                    st.warning("Current price unavailable")
                
                plot_volatility(stock_data)

            # News analysis
            st.header("📰 Latest Market News")
            news = news_analyzer.fetch_financial_news(ticker)
            display_news_with_insights(news)

            # Price prediction
            st.header("🔮 Price Forecast")
            prediction_days = st.slider("Prediction Period (days)", 1, 30, 7)
            predictions = predict_future_prices(stock_data, prediction_days)
            st.plotly_chart(
                create_interactive_chart(predictions),
                use_container_width=True
            )

            # Trading recommendation
            st.header("🤖 Trading Advice")
            recommendation = st.session_state.trading_engine.generate_recommendation(stock_data, news)
            st.success(f"**AI Recommendation:** {recommendation}")

        except Exception as e:
            logger.error(f"Analysis error: {traceback.format_exc()}")
            st.error("Analysis failed. Please try again.")

# ========================================================
# SECTION 5: MAIN APP EXECUTION
# ========================================================

def main():
    """Main application controller"""
    load_css()
    init_session()
    
    if not st.session_state.authenticated:
        login_section()
        st.info("Please login to access the stock advisor")
    else:
        stock_analysis_section()

if __name__ == "__main__":
    main()
