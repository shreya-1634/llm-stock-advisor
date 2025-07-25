import plotly.graph_objects as go
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def plot_candlestick_chart(df: pd.DataFrame, ticker: str):
    """
    Plot candlestick chart with volume bars.
    """
    try:
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlesticks',
            increasing_line_color='green',
            decreasing_line_color='red'
        ))

        fig.update_layout(
            title=f'{ticker.upper()} Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            height=600
        )

        return fig
    except Exception as e:
        logger.error(f"Error generating candlestick chart: {e}")
        return None

def calculate_rsi(df: pd.DataFrame, period: int = 14):
    """
    Calculate Relative Strength Index (RSI).
    """
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_macd(df: pd.DataFrame):
    """
    Calculate MACD and signal line.
    """
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()

    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    return macd, signal

def plot_rsi_macd(df: pd.DataFrame, ticker: str):
    """
    Plot RSI and MACD on a subplot.
    """
    try:
        rsi = calculate_rsi(df)
        macd, signal = calculate_macd(df)

        fig = go.Figure()

        # RSI
        fig.add_trace(go.Scatter(
            x=df.index,
            y=rsi,
            name="RSI",
            line=dict(color='orange')
        ))

        # MACD
        fig.add_trace(go.Scatter(
            x=df.index,
            y=macd,
            name="MACD",
            line=dict(color='cyan')
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=signal,
            name="Signal Line",
            line=dict(color='magenta', dash='dot')
        ))

        fig.update_layout(
            title=f"{ticker.upper()} RSI & MACD",
            xaxis_title='Date',
            yaxis_title='Value',
            template='plotly_dark',
            height=500
        )

        return fig
    except Exception as e:
        logger.error(f"Error generating RSI/MACD chart: {e}")
        return None
