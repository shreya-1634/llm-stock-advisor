import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# API Keys
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "8AUSOBVZ9ASR1SBN")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d1mp259r01qlvnp3rgn0d1mp259r01qlvnp3rgng")


def fetch_from_alpha_vantage(ticker, period):
    try:
        function = "TIME_SERIES_DAILY_ADJUSTED"
        url = f"https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=full"
        r = requests.get(url)
        data = r.json()

        if "Time Series (Daily)" not in data:
            logger.warning("Alpha Vantage data not available or rate limit hit.")
            return pd.DataFrame()

        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        df.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividend", "Split"]
        df = df.astype(float)

        cutoff = datetime.now() - parse_period_to_timedelta(period)
        return df[df.index >= cutoff]
    except Exception as e:
        logger.error(f"Alpha Vantage fetch error: {e}")
        return pd.DataFrame()


def fetch_from_finnhub(ticker, period):
    try:
        end = int(datetime.now().timestamp())
        start = int((datetime.now() - parse_period_to_timedelta(period)).timestamp())
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={FINNHUB_API_KEY}"

        r = requests.get(url)
        data = r.json()

        if data.get("s") != "ok":
            logger.warning("Finnhub data not available or rate limit hit.")
            return pd.DataFrame()

        df = pd.DataFrame({
            "Date": pd.to_datetime(data["t"], unit="s"),
            "Open": data["o"],
            "High": data["h"],
            "Low": data["l"],
            "Close": data["c"],
            "Volume": data["v"]
        }).set_index("Date")

        return df
    except Exception as e:
        logger.error(f"Finnhub fetch error: {e}")
        return pd.DataFrame()


def fetch_from_yfinance(ticker, period):
    try:
        yf_period_map = {
            "7d": "7d", "30d": "1mo", "90d": "3mo", "180d": "6mo", "365d": "1y"
        }
        yf_period = yf_period_map.get(period, "1mo")

        df = yf.download(ticker, period=yf_period)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"YFinance error: {e}")
        return pd.DataFrame()


def parse_period_to_timedelta(period):
    if period == "7d":
        return timedelta(days=7)
    elif period == "30d":
        return timedelta(days=30)
    elif period == "90d":
        return timedelta(days=90)
    elif period == "180d":
        return timedelta(days=180)
    elif period == "365d":
        return timedelta(days=365)
    else:
        return timedelta(days=30)


def fetch_stock_data(ticker, period="30d", source="alpha_vantage"):
    df = pd.DataFrame()
    if source == "alpha_vantage":
        df = fetch_from_alpha_vantage(ticker, period)
    elif source == "finnhub":
        df = fetch_from_finnhub(ticker, period)

    if df.empty:
        df = fetch_from_yfinance(ticker, period)

    return df
