import streamlit as st
import matplotlib.pyplot as plt
from utils import fetch_recent_prices
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="centered")

st.title("🤖 LLM-Powered Stock Advisor")
st.markdown("Enter a stock ticker (e.g., `ADANIENT.NS`, `AAPL`, `TSLA`) and let AI advise whether to **Buy, Sell, or Hold**.")

# Default input
ticker = st.text_input("🔍 Stock Ticker", value="ADANIENT.NS")
submitted = st.button("📊 Analyze")

if submitted:
    with st.spinner("Fetching stock data..."):
        prices = fetch_recent_prices(ticker)

    if prices is None:
        st.warning("⚠️ Failed to fetch stock prices. Make sure the ticker is valid (e.g., `RELIANCE.NS`, `AAPL`).")
    else:
        st.success(f"✅ Retrieved last {len(prices)} days of closing prices for `{ticker}`.")

        # Show line chart
        st.line_chart(prices)

        # Collect additional inputs
        volatility = st.selectbox("Volatility Level", ["Low", "Moderate", "High"])
        news = st.text_area("📰 Recent News Headlines", placeholder="Example:\n- Adani to expand port investment\n- Moody's upgrades stock outlook")

        # Run LLM chain
        with st.spinner("🧠 Thinking..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=f"Last {len(prices)} days: {prices[-5:]} (last 5)",
                volatility_info=volatility,
                news_summary=news or "No major news reported."
            )

        # Display result
        st.markdown("### 🤖 AI Advice")
        st.code(response.strip(), language="markdown")

# Footer
st.caption("Built with ❤️ using Streamlit + LangChain + OpenAI")
