import streamlit as st
import plotly.graph_objects as go
from utils import fetch_recent_prices, fetch_news_headlines
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="centered")
st.title("🤖 LLM-Powered Stock Advisor")
st.markdown("Enter a stock ticker (e.g., `ADANIENT.NS`, `AAPL`, `TSLA`) and let AI analyze trends and news to suggest **Buy, Sell, or Hold**.")

ticker = st.text_input("🔍 Stock Ticker", value="AAPL")
if st.button("📊 Analyze"):
    prices = fetch_recent_prices(ticker)

    if prices is None:
        st.warning("⚠️ Failed to fetch stock prices. Please check the ticker symbol.")
    else:
        st.success(f"✅ Retrieved {len(prices)} prices.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=prices, mode='lines', name=ticker))
        fig.update_layout(title=f"{ticker} Closing Prices", xaxis_title="Days", yaxis_title="Price", hovermode="x")
        st.plotly_chart(fig, use_container_width=True)

        news = fetch_news_headlines(ticker, st.secrets["NEWS_API_KEY"])
        st.markdown("#### 📰 News Headlines")
        st.text(news)

        volatility = st.selectbox("Volatility Level", ["Low", "Moderate", "High"])
        with st.spinner("🧠 Thinking..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=f"Recent closing prices: {prices[-5:]}",
                volatility_info=volatility,
                news_summary=news
            )
        st.markdown("### 🤖 AI Advice")
        st.code(response, language="markdown")
