import streamlit as st
import plotly.graph_objects as go
from utils import fetch_all_prices, fetch_news_with_llm, calculate_volatility
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="centered")
st.title("🤖 LLM-Powered Stock Advisor")

ticker = st.text_input("🔍 Enter stock ticker", value="AAPL")

if st.button("📊 Analyze"):
    with st.spinner("Fetching data..."):
        prices = fetch_all_prices(ticker)

    if prices is None:
        st.warning("⚠️ Failed to fetch stock prices.")
    else:
        st.success(f"✅ Loaded {len(prices)} daily prices.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=prices, mode='lines', name=ticker))
        fig.update_layout(title=f"{ticker} Historical Prices", xaxis_title="Days", yaxis_title="Price", hovermode="x")
        st.plotly_chart(fig, use_container_width=True)

        with st.spinner("Fetching news from web..."):
            news = fetch_news_with_llm(ticker)

        st.subheader("📰 News Summary")
        st.write(news)

        with st.spinner("Calculating volatility..."):
            vol_series = calculate_volatility(prices)
            latest_vol = round(vol_series.iloc[-1], 4) if not vol_series.empty else "Unavailable"

        st.subheader("📉 Volatility Index")
        st.write(f"Latest Volatility: {latest_vol}")

        with st.spinner("🧠 Getting AI analysis..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=str(prices.tail(30).tolist()),
                volatility_info=f"{latest_vol}",
                news_summary=news
            )
        st.subheader("🤖 AI Advice")
        st.markdown(response)
