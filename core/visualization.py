# your_project/core/visualization.py

import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import matplotlib.pyplot as plt

class Visualization:
    def plot_candlestick(self, df: pd.DataFrame, ticker: str):
        if df.empty or 'Open' not in df.columns or 'High' not in df.columns or \
           'Low' not in df.columns or 'Close' not in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No data to plot candlestick.", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"{ticker} Candlestick Chart (No Data)")
            plt.close(fig)
            return fig

        # --- FIX: Ensure the index is a DatetimeIndex and is timezone-naive ---
        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_convert('UTC').tz_localize(None)

        df_mpf = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df_mpf.index.name = 'Date'
        
        apds = []
        if 'RSI' in df.columns and not df['RSI'].isnull().all():
            apds.append(mpf.make_addplot(df['RSI'], panel=1, color='blue', ylabel='RSI'))
        
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns and 'MACD_Diff' in df.columns \
           and not df['MACD'].isnull().all():
            apds.append(mpf.make_addplot(df['MACD'], panel=2, color='green', ylabel='MACD'))
            apds.append(mpf.make_addplot(df['MACD_Signal'], panel=2, color='red'))
            apds.append(mpf.make_addplot(df['MACD_Diff'], panel=2, type='bar', color='gray'))

        fig, axlist = mpf.plot(df_mpf, 
                              type='candle', 
                              style='yahoo', 
                              title=f"{ticker} Candlestick Chart", 
                              ylabel=f"Price", 
                              volume=True, 
                              addplot=apds,
                              returnfig=True, 
                              figscale=1.5)
        plt.close(fig)
        return fig
        
    def plot_interactive_candlestick_plotly(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        if df.empty or 'Open' not in df.columns or 'High' not in df.columns or \
           'Low' not in df.columns or 'Close' not in df.columns:
            return go.Figure().add_annotation(text="No data for interactive candlestick.", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)

        # --- FIX: Ensure the index is a DatetimeIndex and is timezone-naive ---
        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_convert('UTC').tz_localize(None)

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, 
                            row_heights=[0.6, 0.2, 0.2])

        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlesticks'), row=1, col=1)

        if 'RSI' in df.columns and not df['RSI'].isnull().all():
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='blue')), row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1, annotation_text="Oversold", annotation_position="bottom right")
            fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1, annotation_text="Overbought", annotation_position="top right")

        if 'MACD' in df.columns and 'MACD_Signal' in df.columns and 'MACD_Diff' in df.columns \
           and not df['MACD'].isnull().all():
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='green')), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='red')), row=3, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['MACD_Diff'], name='MACD Histogram', marker_color='gray'), row=3, col=1)
            fig.update_yaxes(title_text="MACD", row=3, col=1)

        fig.update_layout(title=f'{ticker} Interactive Stock Analysis',
                          xaxis_rangeslider_visible=False,
                          xaxis_title='Date',
                          yaxis_title='Price',
                          template='plotly_dark',
                          height=700)
        
        return fig

    def plot_prediction_chart(self, historical_df: pd.DataFrame, predicted_series: pd.Series) -> go.Figure:
        if historical_df.empty or predicted_series.empty:
            return go.Figure().add_annotation(text="No data for prediction chart.", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)

        historical_df.index = pd.to_datetime(historical_df.index)
        if historical_df.index.tz is not None:
            historical_df.index = historical_df.index.tz_convert('UTC').tz_localize(None)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=historical_df.index, y=historical_df['Close'], mode='lines', name='Historical Close', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=predicted_series.index, y=predicted_series.values, mode='lines+markers', name='Predicted Close', line=dict(color='orange', dash='dash'), marker=dict(symbol='circle', size=8)))

        fig.update_layout(title='Stock Price Prediction',
                          xaxis_title='Date',
                          yaxis_title='Price',
                          template='plotly_dark',
                          legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top'))
        return fig
