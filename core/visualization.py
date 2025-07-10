import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.config import get_logger

logger = get_logger(__name__)

def create_interactive_chart(data):
    try:
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candlestick"
        ))

        # Moving Averages
        for window in [20, 50]:
            data[f"MA_{window}"] = data['Close'].rolling(window=window).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[f"MA_{window}"],
                name=f"{window}-Day MA",
                line=dict(width=1)
            ))

        # Bollinger Bands
        rolling_mean = data['Close'].rolling(window=20).mean()
        rolling_std = data['Close'].rolling(window=20).std()
        data['Upper'] = rolling_mean + (rolling_std * 2)
        data['Lower'] = rolling_mean - (rolling_std * 2)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Upper'],
            line=dict(color='rgba(173,216,230,0.2)'),
            name='Upper Band'
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Lower'],
            fill='tonexty',
            line=dict(color='rgba(173,216,230,0.2)'),
            name='Lower Band'
        ))

        # MACD
        data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = data['EMA12'] - data['EMA26']
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

        fig.update_layout(
            title="Interactive Stock Chart with Technical Indicators",
            xaxis_rangeslider_visible=True,
            height=700,
            template='plotly_dark',
            hovermode='x unified'
        )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=2, label="2M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            )
        )

        return fig

    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return go.Figure()
