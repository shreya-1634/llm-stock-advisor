import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from core.config import get_logger

logger = get_logger(__name__)

def create_interactive_chart(data):
    try:
        # Indicators
        data['MA_20'] = data['Close'].rolling(window=20).mean()
        data['MA_50'] = data['Close'].rolling(window=50).mean()
        data['BB_STD'] = data['Close'].rolling(window=20).std()
        data['BB_UPPER'] = data['MA_20'] + 2 * data['BB_STD']
        data['BB_LOWER'] = data['MA_20'] - 2 * data['BB_STD']
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        ema12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema26 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = ema12 - ema26
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.55, 0.2, 0.25],
            subplot_titles=["Price & Indicators", "RSI", "MACD"]
        )

        # Row 1: Candlestick + MAs + Bollinger
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candlestick"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data.index, y=data['MA_20'],
            mode='lines', name='MA 20',
            line=dict(color='blue', width=1)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data.index, y=data['MA_50'],
            mode='lines', name='MA 50',
            line=dict(color='orange', width=1)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data.index, y=data['BB_UPPER'],
            mode='lines', name='Bollinger Upper',
            line=dict(color='lightgray', width=1, dash='dot')
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data.index, y=data['BB_LOWER'],
            mode='lines', name='Bollinger Lower',
            line=dict(color='lightgray', width=1, dash='dot')
        ), row=1, col=1)

        # Row 2: RSI
        fig.add_trace(go.Scatter(
            x=data.index, y=data['RSI'],
            mode='lines', name='RSI',
            line=dict(color='purple', width=1)
        ), row=2, col=1)

        fig.add_hline(y=70, line_dash='dot', line_color='red', row=2, col=1)
        fig.add_hline(y=30, line_dash='dot', line_color='green', row=2, col=1)

        # Row 3: MACD + Signal
        fig.add_trace(go.Scatter(
            x=data.index, y=data['MACD'],
            mode='lines', name='MACD',
            line=dict(color='cyan', width=1)
        ), row=3, col=1)

        fig.add_trace(go.Scatter(
            x=data.index, y=data['Signal'],
            mode='lines', name='Signal Line',
            line=dict(color='red', width=1, dash='dash')
        ), row=3, col=1)

        # Layout
        fig.update_layout(
            template="plotly_dark",
            title="📈 Advanced Technical Chart",
            height=900,
            showlegend=True,
            hovermode='x unified',
            margin=dict(t=40, b=40, r=20, l=20),
            xaxis=dict(
                rangeslider=dict(visible=False),
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor="#0e1117",
                    font=dict(color="white")
                )
            ),
            modebar=dict(
                orientation='h',
                bgcolor='#0e1117',
                color='lightgray',
                activecolor='cyan'
            )
        )

        return fig

    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return go.Figure()
