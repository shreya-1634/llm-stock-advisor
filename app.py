import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))  # Fixes import path
import streamlit as st
from datetime import datetime, timedelta
import traceback
from core.config import setup_logging, get_logger
from auth.auth import authenticate_user, logout_user
from core.data_fetcher import fetch_stock_data, get_current_price
from core.visualization import create_interactive_chart, plot_volatility
from core.news_analyzer import news_analyzer, display_news_with_insights
from core.predictor import predict_future_prices
from core.trading_engine import TradingEngine
from auth.permissions import request_permission, check_permission

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Page Configuration
st.set_page_config(
    page_title="AI Stock Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    try:
        with open("static/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        logger.debug("CSS loaded successfully")
    except Exception as e:
        logger.warning(f"CSS load failed: {str(e)}")

def init_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'trading_engine' not in st.session_state:
        st.session_state.trading_engine = None
    if 'current_ticker' not in st.session_state:
        st.session_state.current_ticker = "AAPL"
    logger.debug("Session initialized")

def login_section():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        try:
            if authenticate_user(username, password):
                st.session_state.update({
                    'authenticated': True,
                    'username': username,
                    'trading_engine': TradingEngine(username)
                })
                logger.info(f"User {username} logged in")
                st.rerun()
            else:
                logger.warning(f"Failed login attempt for {username}")
                st.sidebar.error("Invalid credentials")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            st.sidebar.error("Login service unavailable")

def logout_section():
    if st.sidebar.button("Logout"):
        try:
            username = st.session_state.get('username', 'unknown')
            logout_user()
            st.session_state.clear()
            logger.info(f"User {username} logged out")
            st.rerun()
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            st.error("Logout failed. Please try again.")

def stock_analysis_section():
    st.sidebar.title(f"👋 Welcome, {st.session_state.username}")
    logout_section()
    
    st.sidebar.header("Stock Selection")
    ticker = st.sidebar.text_input(
        "Ticker Symbol", 
        value=st.session_state.current_ticker
    ).upper()
    
    date_range = st.sidebar.selectbox(
        "Date Range",
        ["1M", "3M", "6M", "YTD", "1Y", "5Y", "Max"],
        index=2
    )
    
    date_map = {
        "1M": datetime.now() - timedelta(days=30),
        "3M": datetime.now() - timedelta(days=90),
        "6M": datetime.now() - timedelta(days=180),
        "YTD": datetime(datetime.now().year, 1, 1),
        "1Y": datetime.now() - timedelta(days=365),
        "5Y": datetime.now() - timedelta(days=5*365),
        "Max": datetime(1980, 1, 1)
    }

    if st.sidebar.button("Analyze", type="primary"):
        with st.spinner("🧠 Processing data with AI..."):
            try:
                analyze_stock(ticker, date_map[date_range])
            except Exception as e:
                logger.error(f"Analysis failed: {str(e)}\n{traceback.format_exc()}")
                st.error("Analysis failed. Please check logs.")

def analyze_stock(ticker, start_date):
    try:
        logger.info(f"Starting analysis for {ticker}")
        stock_data = fetch_stock_data(ticker, start_date, datetime.now())
        
        if stock_data.empty:
            logger.warning(f"No data found for {ticker}")
            st.error("No data available for this ticker/date range")
            return

        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.plotly_chart(
                create_interactive_chart(stock_data),
                use_container_width=True
            )
        
        with col2:
            try:
                current_price = get_current_price(ticker)
                st.metric("Current Price", f"${current_price:.2f}")
            except Exception as e:
                logger.warning(f"Price fetch failed: {str(e)}")
                st.warning("Current price unavailable")
            
            plot_volatility(stock_data)

        st.header("📰 Latest Market News")
        news = news_analyzer.fetch_financial_news(ticker)
        display_news_with_insights(news)

        st.header("🔮 Price Forecast")
        prediction_days = st.slider(
            "Prediction Period (days)", 
            1, 30, 7
        )
        
        try:
            predictions = predict_future_prices(stock_data, prediction_days)
            st.plotly_chart(
                create_interactive_chart(predictions),
                use_container_width=True
            )
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            st.error("Price prediction service unavailable")

        st.header("🤖 Trading Advice")
        try:
            recommendation = st.session_state.trading_engine.generate_recommendation(
                stock_data, 
                news
            )
            st.success(f"**AI Recommendation:** {recommendation}")

            if recommendation != "HOLD":
                handle_trade_approval(ticker, recommendation)
        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}")
            st.error("Trading advice unavailable")

    except Exception as e:
        logger.error(f"Analysis pipeline failed: {str(e)}")
        st.error("Analysis service currently unavailable")

def handle_trade_approval(ticker, recommendation):
    permission_key = request_permission(
        st.session_state.username,
        recommendation,
        ticker,
        1
    )
    
    if st.button(f"Approve {recomm
