import streamlit as st
import os
from datetime import datetime
from utils import (
    fetch_all_prices,
    fetch_news_with_llm,
    calculate_volatility,
    predict_future_prices,
)
from llm_chain import get_llm_response
import plotly.graph_objects as go

# Load OpenAI API key securely
api_key = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = api_key

# Title and input
st.title("📈 LLM Stock Advisor")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS)", "AAPL").upper()

if ticker:
    # Fetch stock data
    prices = fetch_all_prices(ticker)

    if prices:
        st.subheader(f"📊 Price Chart for {ticker}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices.index, y=prices['Close'], mode='lines', name='Close Price'))
        fig.update_layout(
            xaxis_rangeslider_visible=True,
            xaxis_title='Date',
            yaxis_title='Price (in USD)',
            template='plotly_dark',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Market Volatility
        st.subheader("🌪 Market Volatility")
        vol = calculate_volatility(prices)
        st.write(f"**Volatility Index**: {vol:.2f}")

        # News
        st.subheader("🗞 Recent News")
        news = fetch_news_with_llm(ticker)
        st.write(news or "No major news found.")

        # Future Price Prediction
        st.subheader("🔮 Future Price Prediction")
        future_prices = predict_future_prices(prices)
        st.line_chart(future_prices)

        # LLM Advice
        st.subheader("🤖 AI Advice")
        response = get_llm_response(
            symbol=ticker,
            prices=prices["Close"].tolist(),
            news_summary=news or "No major news available.",
            volatility=vol
        )
        st.success(response)
    else:
        st.error("⚠️ Failed to fetch stock prices. Make sure the ticker is valid (e.g., RELIANCE.NS, AAPL).")
