import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(ticker, period="30d"):
    try:
        # Define the map inside the function
        yf_period_map = {
            "7d": "7d",
            "30d": "1mo",
            "90d": "3mo",
            "180d": "6mo",
            "365d": "1y"
        }

        yf_period = yf_period_map.get(period, "1mo")
        logger.info(f"Fetching {yf_period} data for {ticker} from yfinance")
        df = yf.download(ticker, period=yf_period)
        df.dropna(inplace=True)
        return df

    except Exception as e:
        logger.error(f"YFinance fetch error: {e}")
        return pd.DataFrame()
