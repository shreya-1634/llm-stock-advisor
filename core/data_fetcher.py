import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Map of user-friendly labels to yfinance periods and intervals
yf_config = {
    "1 Day": ("1d", "5m"),
    "5 Days": ("5d", "15m"),
    "1 Week": ("7d", "30m"),
    "1 Month": ("1mo", "1d"),
    "3 Months": ("3mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "2 Years": ("2y", "1d"),
    "5 Years": ("5y", "1wk"),
    "Max": ("max", "1mo")
}

def fetch_stock_data(ticker, label="1 Month"):
    config = yf_config.get(label, {"period": "1mo", "interval": "30m"})
    try:
        logger.info(f"Fetching data for {ticker} with {label}")
        df = yf.download(ticker, period=config["period"], interval=config["interval"])
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"YFinance fetch error: {e}")
        return pd.DataFrame()
