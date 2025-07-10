import streamlit as st
import yfinance as yf
from datetime import datetime
from .config import get_logger

logger = get_logger(__name__)

def fetch_stock_data(ticker, start_date="2022-01-01", end_date=None):
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.warning("🔐 Please login to fetch stock data.")
        st.stop()

    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    try:
        logger.info(f"Fetching stock data for {ticker} from {start_date} to {end_date}")
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            logger.warning(f"No data for {ticker}")
            st.error(f"No data available for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch stock data: {str(e)}")
        st.error("Failed to fetch data. Please try again.")
        return None

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period='1d')['Close'].iloc[-1]
        logger.info(f"Current price of {ticker}: {price}")
        return price
    except Exception as e:
        logger.error(f"Error fetching current price: {str(e)}")
        return None
