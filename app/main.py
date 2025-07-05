import streamlit as st
import os
import sys
import plotly.graph_objs as go

# Set Python path to include current directory
sys.path.append(os.path.dirname(__file__))

# Load OpenAI key from secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Local imports
from utils import (
    fetch_all_prices,
    fetch_news_with_links,
    calculate_volatility,
    predict_future_prices
)
from llm_chain import get_llm_response

# Streamlit app config
st.set_page_config(page_title="LLM Stock Advisor", layout="wide")
st.title("📈 LLM-Powered Stock Advisor")

# User input
ticker = st.text_input("Enter stock ticker symbol (e.g., AAPL, RELIANCE.NS)", "AAPL")

# Fetch stock prices
prices = fetch_all_prices(ticker)
if prices is None:
    st.error("⚠️ Failed to fetch stock prices. Make sure the ticker is valid.")
    st.stop()

# Prepare DataFrame
df = prices.rename(columns={"Close": "Price"})
df["Date"] = df.index

# Draw Plotly chart (Google Finance-style)
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Price"], mode="lines", name="Price"))
fig.update_layout(
    title=f"{ticker.upper()} Price History",
    xaxis_title="Date",
    yaxis_title="Price (in local currency)",
    xaxis=dict(rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(step="all")
        ])
    ), rangeslider=dict(visible=True), type="date"),
    template="plotly_white",
    height=500,
)
st.plotly_chart(fig, use_container_width=True)

# Calculate and show volatility
volatility = calculate_volatility(prices)
st.subheader("📉 Market Volatility")
st.write(f"Standard deviation of daily returns: **{volatility:.2f}%**")

# Fetch news with links
news = fetch_news_with_links(ticker)
if news:
    st.subheader("📰 Recent News Headlines")
    for headline, link in news:
        st.markdown(f"- [{headline}]({link})")
else:
    st.warning("No recent news headlines found.")

# Predict future prices
future_prices = predict_future_prices(prices)
if future_prices is not None:
    st.subheader("🔮 Future Price Prediction")
    future_fig = go.Figure()
    future_fig.add_trace(go.Scatter(x=future_prices.index, y=future_prices.values, mode="lines+markers", name="Predicted"))
    future_fig.update_layout(
        title="Predicted Future Prices (Next 7 Days)",
        xaxis_title="Date",
        yaxis_title="Predicted Price",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(future_fig, use_container_width=True)

# AI recommendation using LLM
st.subheader("🤖 AI Recommendation")
if st.button("Get AI Advice"):
    with st.spinner("Thinking..."):
        response = get_llm_response(
            symbol=ticker,
            volatility=f"{volatility:.2f}",
            news_summary=" ".join([n[0] for n in news]) if news else "No news available",
        )
    st.success("AI Advice")
    st.markdown(response)

# User approval for AI to act
st.subheader("🛡️ Allow AI to Take Action?")
decision = st.radio("Would you like to allow the AI to automatically act on its recommendation?", ["No", "Yes"], index=0)

if decision == "Yes":
    st.success("✅ AI will proceed with Buy/Sell/Hold based on its recommendation.")
else:
    st.info("ℹ️ AI will not take action without user permission.")
