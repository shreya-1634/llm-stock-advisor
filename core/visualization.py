# core/visualization.py

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.config import get_logger

logger = get_logger(__name__)

def create_interactive_chart(data):
    try:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlestick'
        )])

        # Moving Averages
        for window in [20, 50]:
            data[f'MA_{window}'] = data['Close'].rolling(window=window).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[f'MA_{window}'],
                name=f'{window}-Day MA',
                line=dict(width=1)
            ))

        fig.update_layout(
            title='Stock Price with Moving Averages',
            xaxis_rangeslider_visible=True,
            template='plotly_dark',
            height=600,
            hovermode='x unified'
        )

        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        logger.debug("Main chart generated")
        return fig

    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return go.Figure()

def plot_rsi(data, window=14):
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['RSI'],
            name='RSI',
            line=dict(color='cyan', width=2)
        ))
        fig.add_hline(y=70, line_dash="dot", line_color="red")
        fig.add_hline(y=30, line_dash="dot", line_color="green")

        fig.update_layout(
            title='Relative Strength Index (RSI)',
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        logger.debug("RSI chart generated")
        return fig
    except Exception as e:
        logger.error(f"RSI chart failed: {str(e)}")
        return go.Figure()

def plot_macd(data):
    try:
        ema12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=macd,
            name='MACD',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=signal,
            name='Signal Line',
            line=dict(color='orange')
        ))

        fig.update_layout(
            title='MACD (Moving Average Convergence Divergence)',
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        logger.debug("MACD chart generated")
        return fig
    except Exception as e:
        logger.error(f"MACD chart failed: {str(e)}")
        return go.Figure()

def plot_volatility(data):
    # Compute daily return
    data['Daily_Return'] = data['Close'].pct_change()

    # Compute annualized volatility
    data['Volatility'] = data['Daily_Return'].rolling(window=20).std() * np.sqrt(252)

    # Compute RSI (14-day)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Compute Bollinger Bands (20-day moving average and std dev)
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['Upper_Band'] = data['MA20'] + 2 * data['Close'].rolling(window=20).std()
    data['Lower_Band'] = data['MA20'] - 2 * data['Close'].rolling(window=20).std()

    fig = go.Figure()

    # Volatility line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Volatility'],
        name='Volatility (20D)',
        line=dict(color='orange', width=2)
    ))

    # RSI line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['RSI'],
        name='RSI (14D)',
        line=dict(color='cyan', width=2)
    ))

    # Bollinger Band (Upper)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Upper_Band'],
        name='Bollinger Upper',
        line=dict(color='lightgreen', dash='dash')
    ))

    # Bollinger Band (Lower)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Lower_Band'],
        name='Bollinger Lower',
        line=dict(color='lightcoral', dash='dash')
    ))

    fig.update_layout(
        title="Volatility, RSI & Bollinger Bands",
        xaxis_title="Date",
        yaxis_title="Value",
        template='plotly_dark',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig
