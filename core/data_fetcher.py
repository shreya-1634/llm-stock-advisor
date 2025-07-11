import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Google Finance-style time ranges
yf_config = {
    "1 Day": {"period": "1d", "interval": "1h"},
    "5 Days": {"period": "5d", "interval": "30m"},
    "1 Month": {"period": "1mo", "interval": "1d"},
    "3 Months": {"period": "3mo", "interval": "1d"},
    "6 Months": {"period": "6mo", "interval": "1d"},
    "1 Year": {"period": "1y", "interval": "1d"},
    "5 Years": {"period": "5y", "interval": "1wk"},
    "Max": {"period": "max", "interval": "1mo"}
}

def fetch_stock_data(ticker, range_label):
    try:
        config = yf_config.get(range_label, {"period": "1mo", "interval": "1d"})
        logger.info(f"Fetching data for {ticker} with {range_label}")
        df = yf.download(ticker, period=config["period"], interval=config["interval"])
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"YFinance fetch error: {e}")
        return pd.DataFrame()
