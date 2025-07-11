import plotly.graph_objects as go
import pandas as pd

def create_interactive_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Candlesticks"
    ))

    fig.update_layout(
        title=f"{ticker.upper()} - Stock Price",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )
    return fig

def plot_macd(df):
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=macd, name='MACD Line', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=signal, name='Signal Line', line=dict(color='orange')))

    fig.update_layout(title="MACD Indicator", template="plotly_dark")
    return fig

def plot_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI", line=dict(color='green')))
    fig.update_layout(title="RSI Indicator", yaxis_title="RSI", template="plotly_dark")
    return fig
