import streamlit as st
import os
import sys
import plotly.graph_objects as go

# Add app directory to path for utils import
sys.path.append(os.path.dirname(__file__))

from utils import (
    fetch_all_prices,
    fetch_news_with_links,
    calculate_volatility,
    predict_future_prices,
)
from llm_chain import get_llm_response

# Load API key from Streamlit secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(layout="wide", page_title="LLM Stock Advisor", page_icon="📈")
st.title("📊 LLM-Powered Stock Advisor")

# 🏷️ Stock ticker input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS)", value="AAPL")

# 📥 Fetch stock data
prices = fetch_all_prices(ticker)

if prices is not None and not prices.empty:
    # Format DataFrame for chart
    df = prices.copy()
    df = df.reset_index()
    df.columns = ["Date", "Price"]

    # 📉 Show chart like Google Finance
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Price"], mode="lines", name=ticker))
    fig.update_layout(
        title="Stock Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=True,
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
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# 📊 Volatility
st.subheader("📈 Market Volatility")
volatility = calculate_volatility(prices)

if isinstance(volatility, (int, float)):
    st.write(f"Standard deviation of daily returns: **{volatility:.2f}%**")
else:
    st.warning("Could not calculate volatility.")


    # 📰 Fetch and show news
    st.subheader("🗞️ Recent News")
    news_links, summarized_news = fetch_news_with_links(ticker)
    if summarized_news:
        for title, link in news_links:
            st.markdown(f"- [{title}]({link})")
    else:
        st.info("No relevant news found.")

    # 🔮 Predict future prices
    future = predict_future_prices(prices)
    if future is not None:
        st.subheader("🔮 Predicted Future Prices")
        st.line_chart(future)

    # 🤖 AI Advice with user control
    st.subheader("🤖 AI Investment Suggestion")
    ai_advice = get_llm_response(
        symbol=ticker,
        news_summary=summarized_news or "No major news reported.",
        prices=prices
    )
    st.write("### Suggestion:")
    st.markdown(ai_advice)

    # 🔐 User consent for execution
    if st.toggle("Give AI Permission to Act on Advice"):
        if "buy" in ai_advice.lower():
            st.success("✅ Executing BUY order... (simulated)")
        elif "sell" in ai_advice.lower():
            st.warning("⚠️ Executing SELL order... (simulated)")
        elif "hold" in ai_advice.lower():
            st.info("🕒 Holding position... (simulated)")
        else:
            st.error("❌ No clear action found in AI advice.")
    else:
        st.info("Waiting for user permission to act.")
else:
    st.error("⚠️ Failed to fetch stock data. Make sure the ticker is valid.")
