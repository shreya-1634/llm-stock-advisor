from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.config import get_logger

logger = get_logger(__name__)

def create_interactive_chart(data):
    try:
        # Moving Averages
        data['MA_20'] = data['Close'].rolling(window=20).mean()
        data['MA_50'] = data['Close'].rolling(window=50).mean()

        # Bollinger Bands
        data['BB_MID'] = data['MA_20']
        data['BB_STD'] = data['Close'].rolling(window=20).std()
        data['BB_UPPER'] = data['BB_MID'] + 2 * data['BB_STD']
        data['BB_LOWER'] = data['BB_MID'] - 2 * data['BB_STD']

        # RSI (Relative Strength Index)
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema26 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = ema12 - ema26
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

        # Plotly figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.05,
                            row_heights=[0.6, 0.2, 0.2],
                            subplot_titles=("Price Chart with Indicators", "RSI", "MACD"))

        # Row 1: Candlestick + MAs + Bollinger Bands
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'],
            name="Candlestick"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(x=data.index, y=data['MA_20'],
                                 name='20-Day MA', line=dict(color='blue', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA_50'],
                                 name='50-Day MA', line=dict(color='orange', width=1)), row=1, col=1)

        fig.add_trace(go.Scatter(x=data.index, y=data['BB_UPPER'],
                                 name='Bollinger Upper', line=dict(color='lightgray', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_LOWER'],
                                 name='Bollinger Lower', line=dict(color='lightgray', width=1)), row=1, col=1)

        # Row 2: RSI
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'],
                                 name='RSI', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line_dash='dash', line_color='red', row=2, col=1)
        fig.add_hline(y=30, line_dash='dash', line_color='green', row=2, col=1)

        # Row 3: MACD
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'],
                                 name='MACD', line=dict(color='black')), row=3, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal'],
                                 name='Signal Line', line=dict(color='red')), row=3, col=1)

        # Layout
        fig.update_layout(
            height=900,
            template='plotly_dark',
            title='📊 Advanced Stock Chart',
            hovermode='x unified',
            xaxis_rangeslider_visible=False
        )

        return fig

    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return go.Figure()
