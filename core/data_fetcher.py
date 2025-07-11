import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(ticker, period="1mo", interval="1d"):
    try:
        logger.info(f"Fetching data for {ticker} with {period}, {interval}")
        df = yf.download(ticker, period=period, interval=interval)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"YFinance fetch error: {e}")
        return pd.DataFrame()
