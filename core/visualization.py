import plotly.graph_objects as go
import pandas as pd
import numpy as np
from .config import get_logger

logger = get_logger(__name__)

def create_interactive_chart(data, ticker):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    ))

    # Moving Averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], mode='lines', name='MA20', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='MA50', line=dict(color='red')))

    # Bollinger Bands
    data['STD'] = data['Close'].rolling(window=20).std()
    data['Upper'] = data['MA20'] + 2 * data['STD']
    data['Lower'] = data['MA20'] - 2 * data['STD']

    fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], name='Upper Band', line=dict(color='gray', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], name='Lower Band', line=dict(color='gray', dash='dot')))

    fig.update_layout(
        title=f'📈 {ticker} Candlestick Chart with MA & Bollinger Bands',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600
    )

    return fig


def plot_rsi(data):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI', line=dict(color='orange')))
    fig.add_hline(y=70, line=dict(color='red', dash='dash'))
    fig.add_hline(y=30, line=dict(color='green', dash='dash'))

    fig.update_layout(
        title="RSI (Relative Strength Index)",
        template="plotly_dark",
        height=300
    )

    return fig


def plot_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=macd, name='MACD', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=data.index, y=signal, name='Signal', line=dict(color='magenta')))

    fig.update_layout(
        title="MACD (Moving Average Convergence Divergence)",
        template="plotly_dark",
        height=300
    )

    return fig


def plot_volatility(data):
    import plotly.graph_objs as go
    import pandas as pd

    data['Returns'] = data['Close'].pct_change()
    data['Volatility'] = data['Returns'].rolling(window=10).std()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Volatility'],
                             mode='lines', name='Volatility'))

    fig.update_layout(title="Volatility Over Time",
                      xaxis_title='Date',
                      yaxis_title='Volatility')
    return fig

    except Exception as e:
        logger.error(f"Volatility plot failed: {str(e)}")
        return go.Figure()
