import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.config import get_logger

logger = get_logger(__name__)

def calculate_indicators(data):
    # Bollinger Bands
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['STD20'] = data['Close'].rolling(window=20).std()
    data['Upper'] = data['MA20'] + (2 * data['STD20'])
    data['Lower'] = data['MA20'] - (2 * data['STD20'])

    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    return data

def create_interactive_chart(data, period="6mo"):
    try:
        data = calculate_indicators(data)

        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlestick'
        ))

        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Upper'],
            line=dict(color='rgba(173,216,230,0.3)', width=1),
            name='Upper Band'
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Lower'],
            line=dict(color='rgba(173,216,230,0.3)', width=1),
            name='Lower Band',
            fill='tonexty',
            fillcolor='rgba(173,216,230,0.1)'
        ))

        # Moving averages
        for ma in [20, 50]:
            data[f'MA_{ma}'] = data['Close'].rolling(window=ma).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[f'MA_{ma}'],
                mode='lines',
                name=f'{ma}-Day MA',
                line=dict(width=1)
            ))

        # Layout and time filter buttons
        fig.update_layout(
            title='📈 Stock Price Chart with Indicators',
            xaxis_rangeslider_visible=True,
            template='plotly_dark',
            hovermode='x unified',
            height=600,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=2, label="2M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True)
            )
        )
        return fig
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return go.Figure()

def plot_volatility(data):
    try:
        data['Daily_Return'] = data['Close'].pct_change()
        data['Volatility'] = data['Daily_Return'].rolling(window=20).std() * np.sqrt(252)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Volatility'],
            name='Volatility',
            line=dict(color='orange')
        ))

        fig.update_layout(
            title='📊 Volatility (20-day Rolling)',
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        return fig
    except Exception as e:
        logger.error(f"Volatility plot failed: {str(e)}")
        return go.Figure()

def plot_rsi(data):
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['RSI'],
            name='RSI',
            line=dict(color='cyan')
        ))
        fig.add_hline(y=70, line=dict(dash='dash', color='red'))
        fig.add_hline(y=30, line=dict(dash='dash', color='green'))

        fig.update_layout(
            title='💡 Relative Strength Index (RSI)',
            template='plotly_dark',
            height=300
        )
        return fig
    except Exception as e:
        logger.error(f"RSI plot failed: {str(e)}")
        return go.Figure()

def plot_macd(data):
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD'],
            name='MACD',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Signal'],
            name='Signal Line',
            line=dict(color='orange')
        ))

        fig.update_layout(
            title='📊 MACD (Moving Average Convergence Divergence)',
            template='plotly_dark',
            height=300
        )
        return fig
    except Exception as e:
        logger.error(f"MACD plot failed: {str(e)}")
        return go.Figure()
