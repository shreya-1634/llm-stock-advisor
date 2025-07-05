import streamlit as st
import os
import sys
import pandas as pd
import plotly.graph_objects as go

# Add current directory to sys.path to import utils correctly
sys.path.append(os.path.dirname(__file__))

from utils import (
    fetch_all_prices,
    fetch_news_with_links,
    calculate_volatility,
    predict_future_prices,
    ai_decision_suggestion
)

# Load OpenAI key securely from Streamlit secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# App Title
st.set_page_config(page_title="📈 LLM Stock Advisor", layout="wide")
st.title("📈 LLM-Powered Stock Advisor")

# Input section
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, RELIANCE.NS):", value="AAPL")

# Fetch data
prices = fetch_all_prices(ticker)
news_items = fetch_news_with_links(ticker)
volatility = calculate_volatility(prices)
future = predict_future_prices(prices)
ai_advice = ai_decision_suggestion(news_items, prices)

if prices is not None:
    df = pd.DataFrame({"Price": prices})
    df.index.name = "Date"
    df.reset_index(inplace=True)

    # Chart with zoom features like Google Finance
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Price"], mode="lines", name=ticker))
    fig.update_layout(
        title=f"{ticker} Stock Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis=dict(rangeselector=dict(
            buttons=list([
                dict(count=1, label="1D", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ), rangeslider=dict(visible=True), type="date")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show volatility
    if volatility is not None:
        st.subheader("📊 Market Volatility")
        st.write(f"Standard deviation of daily returns: **{volatility:.2f}%**")
    else:
        st.warning("⚠️ Could not compute volatility.")

    # Show news headlines
    st.subheader("📰 Recent News")
    if news_items:
        for item in news_items:
            st.markdown(f"- [{item['title']}]({item['link']})")
    else:
        st.write("No news found.")

    # Show AI prediction
    st.subheader("🤖 AI Prediction")
    st.markdown(f"**Suggested Action:** {ai_advice.upper()}")

    # Show future predicted prices
    if future is not None:
        st.subheader("🔮 Predicted Future Prices")
        future_df = pd.DataFrame(future, columns=["Predicted Price"])
        future_df.index.name = "Date"
        st.line_chart(future_df)

    # AI Permission Section
    st.subheader("🔐 Allow AI to Take Action?")
    ai_access = st.checkbox("I allow the AI to make the Buy/Sell/Hold decision for me.")
    if ai_access:
        st.success(f"✅ AI has been granted permission to act.")
        st.write(f"Action: **{ai_advice.upper()}** will be initiated.")
    else:
        st.warning("⚠️ AI permission not granted. No action will be taken.")

else:
    st.error("❌ Failed to fetch stock prices. Please check the ticker symbol.")
