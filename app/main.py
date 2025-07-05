import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Ensure current directory is in path to find utils
sys.path.append(os.path.dirname(__file__))

from utils import (
    fetch_all_prices,
    fetch_news_with_links,
    calculate_volatility,
    predict_future_prices
)
from llm_chain import get_llm_response

# --- Set API key from Streamlit secrets ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")

# --- User input ---
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS):", value="AAPL")

# --- Fetch data ---
prices = fetch_all_prices(ticker)
news = fetch_news_with_links(ticker)
volatility = calculate_volatility(prices)

if prices is not None:
    df = prices.to_frame(name="Price")
    df.index = pd.to_datetime(df.index)

    # --- Plot Google Finance-like Chart ---
    st.subheader("📊 Stock Price Chart")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Price'], name="Price"))
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis_title="Price (USD/INR)",
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Show Market Volatility ---
    if volatility is not None:
        st.subheader("📉 Market Volatility")
        st.write(f"Standard deviation of daily returns: **{volatility:.2f}%**")
    else:
        st.warning("Volatility could not be calculated.")

    # --- Predict future prices ---
    st.subheader("🔮 Future Price Prediction")
    future = predict_future_prices(df)
    if future is not None:
        st.line_chart(future, use_container_width=True)
    else:
        st.warning("Could not generate future prediction.")

    # --- News Section ---
    st.subheader("🗞️ Market News")
    if news:
        for item in news:
            st.markdown(f"- [{item['title']}]({item['url']})")
    else:
        st.info("No recent news found.")

    # --- AI Suggestion ---
    st.subheader("🤖 AI Advice")
    ai_response = get_llm_response(
        symbol=ticker,
        price_data=df.to_dict(),
        news_summary="\n".join([item['title'] for item in news]) or "No major news."
    )
    st.success(ai_response)

    # --- User Control for AI Execution ---
    if "allow_trade" not in st.session_state:
        st.session_state.allow_trade = False

    if st.button("Allow AI to Execute Trade Decision"):
        st.session_state.allow_trade = True

    if st.session_state.allow_trade:
        st.info("✅ AI has permission to act on your behalf.")
        st.write("Executing decision... (simulated)")
    else:
        st.warning("❌ AI does not have permission to execute trade.")
else:
    st.error("⚠️ Failed to fetch stock prices. Make sure the ticker is valid (e.g., RELIANCE.NS, AAPL).")
