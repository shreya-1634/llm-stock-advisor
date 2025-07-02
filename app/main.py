import streamlit as st
import json
from utils import fetch_recent_prices
from llm_chain import get_llm_response

st.set_page_config(page_title="LLM Stock Forecast Advisor", layout="centered")
st.title("📈 LLM-Powered Stock Forecast Advisor")

ticker = st.text_input("Enter Stock Ticker", value="RELIANCE.NS")

sample_news = [
    "Reliance announces major investment in green energy.",
    "Market opens flat despite strong tech rally."
]

if st.button("Run Forecast"):
    prices = fetch_recent_prices(ticker)

    if not prices:
        st.error("⚠️ Failed to fetch stock prices.")
    else:
        with st.spinner("🔮 Asking GPT..."):
            response = get_llm_response(ticker, prices, sample_news)

        st.subheader("📊 Forecast + Recommendation")
        try:
            parsed = json.loads(response)
            st.json(parsed)
        except json.JSONDecodeError:
            st.error("⚠️ GPT returned invalid JSON. Showing plain text:")
            st.code(response, language="text")
