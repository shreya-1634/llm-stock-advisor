import plotly.graph_objects as go
import pandas as pd

def plot_candlestick(df: pd.DataFrame, ticker: str):
    """
    Plots candlestick chart with volume.
    """
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    ))

    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Volume'],
        name='Volume',
        marker_color='lightblue',
        yaxis='y2'
    ))

    fig.update_layout(
        title=f'{ticker.upper()} Stock Price & Volume',
        yaxis_title='Price',
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        xaxis_rangeslider_visible=False,
        height=600
    )

    return fig


def plot_rsi(df: pd.DataFrame, ticker: str):
    """
    Plots RSI (Relative Strength Index).
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['RSI'],
        name='RSI',
        line=dict(color='purple')
    ))

    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought", annotation_position="top left")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold", annotation_position="bottom left")

    fig.update_layout(
        title=f'{ticker.upper()} RSI (Relative Strength Index)',
        yaxis_title='RSI',
        xaxis_title='Date',
        height=400
    )

    return fig


def plot_macd(df: pd.DataFrame, ticker: str):
    """
    Plots MACD and Signal Line.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MACD'],
        name='MACD',
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Signal_Line'],
        name='Signal Line',
        line=dict(color='orange')
    ))

    fig.update_layout(
        title=f'{ticker.upper()} MACD & Signal Line',
        yaxis_title='MACD',
        xaxis_title='Date',
        height=400
    )

    return fig
