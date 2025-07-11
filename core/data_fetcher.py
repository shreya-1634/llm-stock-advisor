import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def fetch_from_yfinance(ticker, period_label):
    try:
        # Mapping like Google Finance
        yf_period_map = {
            "1 Day": ("1d", "1h"),
            "5 Days": ("5d", "30m"),
            "1 Week": ("7d", "1h"),
            "1 Month": ("1mo", "1d"),
            "3 Months": ("3mo", "1d"),
            "6 Months": ("6mo", "1d"),
            "1 Year": ("1y", "1d"),
            "2 Years": ("2y", "1d"),
            "5 Years": ("5y", "1wk"),
            "10 Years": ("10y", "1mo"),
            "Year to Date": ("ytd", "1d"),
            "Max": ("max", "1mo")
        }

        period, interval = yf_period_map.get(period_label, ("1mo", "1d"))

        logger.info(f"Fetching data for {ticker} with period='{period}', interval='{interval}'")

        df = yf.download(ticker, period=period, interval=interval)
        df.dropna(inplace=True)
        return df

    except Exception as e:
        logger.error(f"YFinance fetch error: {e}")
        return pd.DataFrame()


def fetch_stock_data(ticker, period_label="1 Month"):
    """
    Fetch stock data using yfinance only.
    :param ticker: Stock ticker symbol (e.g., AAPL)
    :param period_label: User-friendly time range label
    :return: DataFrame with stock data
    """
    return fetch_from_yfinance(ticker, period_label)
