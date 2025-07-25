import yfinance as yf
import pandas as pd
import numpy as np
from core.config import get_logger

logger = get_logger(__name__)

def fetch_stock_data(ticker: str, period="6mo", interval="1d") -> pd.DataFrame:
    """
    Fetch historical stock data for a given ticker using yfinance.
    """
    try:
        logger.info(f"Fetching data for {ticker}")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            raise ValueError(f"No data found for {ticker}")

        df.reset_index(inplace=True)
        df.dropna(inplace=True)
        df["Ticker"] = ticker.upper()

        return df

    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Compute the Relative Strength Index (RSI).
    """
    logger.debug("Calculating RSI...")
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df['RSI'] = rsi
    return df


def compute_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute MACD and Signal Line.
    """
    logger.debug("Calculating MACD...")
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()

    df['MACD'] = macd
    df['Signal_Line'] = signal
    return df
