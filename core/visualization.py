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
            close=data['Close']
        )])
        
        for window in [20, 50]:
            data[f'MA_{window}'] = data['Close'].rolling(window=window).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[f'MA_{window}'],
                name=f'{window}-Day MA',
                line=dict(width=1)
            ))
        
        fig.update_layout(
            title='Interactive Stock Chart',
            xaxis_rangeslider_visible=True,
            template='plotly_dark',
            height=600,
            hovermode='x unified'
        )
        
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        logger.debug("Chart generated successfully")
        return fig
        
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return go.Figure()

def plot_volatility(data):
    try:
        data['Daily_Return'] = data['Close'].pct_change()
        data['Volatility'] = data['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Volatility'],
            name='Annualized Volatility',
            line=dict(color='orange', width=2)
        ))
        
        fig.update_layout(
            height=300,
            showlegend=True,
            template='plotly_dark',
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        logger.debug("Volatility plot generated")
        return fig
        
    except Exception as e:
        logger.error(f"Volatility plot failed: {str(e)}")
        return go.Figure()
