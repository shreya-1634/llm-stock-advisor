import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

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

def fetch_stock_data(ticker, period="30d"):
    try:
        yf_period = yf_period_map.get(period, "1mo")
        logger.info(f"Fetching {yf_period} data for {ticker} from yfinance")
        df = yf.download(ticker, period=yf_period)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"YFinance fetch error: {e}")
        return pd.DataFrame()

