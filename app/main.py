import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    fetch_all_prices,
    fetch_news_with_llm,
    calculate_volatility,
    predict_future_prices
)
import datetime

# Title
st.set_page_config(page_title="LLM Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")
st.markdown("Get data-driven advice powered by AI on your favorite stocks.")

# User input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS):", "AAPL")

if ticker:
    prices = fetch_all_prices(ticker)

    if prices is not None:
        # Price chart
        st.subheader("📊 Historical Stock Price")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prices.index, y=prices.values,
            mode='lines',
            name='Close Price'
        ))
        fig.update_layout(
            xaxis_rangeslider_visible=True,
            xaxis_title='Date',
            yaxis_title='Price',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Volatility
        st.subheader("📉 Market Volatility")
        vol = calculate_volatility(prices)
        st.write(f"**Volatility:** {vol:.4f}")

        # Future predictions
        st.subheader("🔮 Future Price Prediction (next 5 days)")
        future = predict_future_prices(prices.to_frame(name="Close"))
        future_df = pd.DataFrame({
            "Date": pd.date_range(prices.index[-1] + datetime.timedelta(days=1), periods=5),
            "Predicted Price": future
        })
        st.table(future_df.set_index("Date"))

        # News headlines
        st.subheader("📰 Latest News Headlines")
        api_key = st.secrets["OPENAI_API_KEY"]
        news_summary = fetch_news_with_llm(ticker, api_key)
        st.write(news_summary)

        # AI suggestion
        st.subheader("🤖 AI Investment Suggestion")
        suggestion = ""
        if vol > 0.03:
            suggestion = "High volatility detected. ⚠️ Consider HOLD or SELL."
        elif future[-1] > prices.values[-1] * 1.03:
            suggestion = "Uptrend predicted 📈 — Consider BUY."
        elif future[-1] < prices.values[-1] * 0.97:
            suggestion = "Downtrend predicted 📉 — Consider SELL."
        else:
            suggestion = "Stable forecast — Consider HOLD."

        st.markdown(f"**{suggestion}**")

    else:
        st.error("⚠️ Failed to fetch stock prices. Make sure the ticker is valid.")
