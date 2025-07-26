# your_project/core/visualization.py

import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import matplotlib.pyplot as plt # For mplfinance to return a figure

class Visualization:
    def plot_candlestick(self, df: pd.DataFrame, ticker: str):
        """
        Generates a static candlestick chart with optional RSI and MACD panels using mplfinance.
        Returns a matplotlib figure.
        """
        if df.empty or 'Open' not in df.columns or 'High' not in df.columns or \
           'Low' not in df.columns or 'Close' not in df.columns:
            print("Not enough data to plot static candlestick.")
            fig, ax = plt.subplots() # Return an empty figure
            ax.text(0.5, 0.5, "No data to plot", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            return fig

        # Ensure correct column names for mplfinance and index is datetime
        df_mpf = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df_mpf.index.name = 'Date'
        df_mpf.index = pd.to_datetime(df_mpf.index) # Ensure datetime index

        apds = [] # Additional plots for indicators
        
        # Add RSI panel if available
        if 'RSI' in df.columns and not df['RSI'].isnull().all():
            apds.append(mpf.make_addplot(df['RSI'], panel=1, color='blue', ylabel='RSI'))
        
        # Add MACD panel if available
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns and 'MACD_Diff' in df.columns \
           and not df['MACD'].isnull().all():
            apds.append(mpf.make_addplot(df['MACD'], panel=2, color='green', ylabel='MACD'))
            apds.append(mpf.make_addplot(df['MACD_Signal'], panel=2, color='red'))
            apds.append(mpf.make_addplot(df['MACD_Diff'], panel=2, type='bar', color='gray'))

        # Create the plot and return the figure
        fig, axlist = mpf.plot(df_mpf, 
                          type='candle', 
                          style='yahoo', # Or 'charles', 'binance', etc.
                          title=f"{ticker} Candlestick Chart", 
                          ylabel='Price', 
                          volume=True, 
                          addplot=apds,
                          returnfig=True, # Important to return the figure for Streamlit
                          figscale=1.5) # Scale figure for better visibility in Streamlit
        return fig

    def plot_interactive_candlestick_plotly(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        """
        Generates an interactive candlestick chart using Plotly, with RSI and MACD subplots.
        """
        if df.empty or 'Open' not in df.columns or 'High' not in df.columns or \
           'Low' not in df.columns or 'Close' not in df.columns:
            print("No data to plot interactive candlestick.")
            return go.Figure()

        # Create subplots: 3 rows for Price, RSI, MACD
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, 
                            row_heights=[0.6, 0.2, 0.2])

        # Candlestick chart
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'],
                                     name='Candlesticks'), row=1, col=1)

        # RSI plot
        if 'RSI' in df.columns and not df['RSI'].isnull().all():
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', 
                                     name='RSI', line=dict(color='blue')), row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1, annotation_text="Oversold", annotation_position="bottom right")
            fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1, annotation_text="Overbought", annotation_position="top right")


        # MACD plot
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns and 'MACD_Diff' in df.columns \
           and not df['MACD'].isnull().all():
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', 
                                     name='MACD', line=dict(color='green')), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', 
                                     name='MACD Signal', line=dict(color='red')), row=3, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['MACD_Diff'], name='MACD Histogram', 
                                 marker_color='gray'), row=3, col=1)
            fig.update_yaxes(title_text="MACD", row=3, col=1)

        fig.update_layout(title=f'{ticker} Interactive Stock Analysis',
                          xaxis_rangeslider_visible=False, # Hide range slider for cleaner view
                          xaxis_title='Date',
                          yaxis_title='Price',
                          template='plotly_dark', # Or 'plotly_white' based on your preference
                          height=700) # Adjust height as needed
        
        return fig

    def plot_prediction_chart(self, historical_df: pd.DataFrame, predicted_series: pd.Series) -> go.Figure:
        """
        Plots historical close prices and future predicted prices.
        """
        if historical_df.empty or predicted_series.empty:
            return go.Figure().add_annotation(text="No data for prediction chart", showarrow=False)

        fig = go.Figure()

        # Historical Close Prices
        fig.add_trace(go.Scatter(x=historical_df.index, y=historical_df['Close'],
                                 mode='lines', name='Historical Close',
                                 line=dict(color='blue')))

        # Predicted Prices
        fig.add_trace(go.Scatter(x=predicted_series.index, y=predicted_series.values,
                                 mode='lines+markers', name='Predicted Close',
                                 line=dict(color='orange', dash='dash'),
                                 marker=dict(symbol='circle', size=8)))

        fig.update_layout(title='Stock Price Prediction',
                          xaxis_title='Date',
                          yaxis_title='Price',
                          template='plotly_dark',
                          legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top'))
        return fig
