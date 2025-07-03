import streamlit as st
import plotly.graph_objects as go
from utils import fetch_all_prices, fetch_news_with_llm, calculate_volatility
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="centered")
st.title("🤖 LLM-Powered Stock Advisor")

ticker = st.text_input("🔍 Enter stock ticker", value="AAPL")

if st.button("📊 Analyze"):
    with st.spinner("📥 Fetching stock price history..."):
        prices = fetch_all_prices(ticker)

    if prices is None or prices.empty:
        st.warning("⚠️ Could not retrieve stock data. Check the ticker symbol.")
    else:
        st.success(f"✅ Retrieved {len(prices)} price records.")

        # Display sample data
        st.write("📊 Sample closing prices:", prices.tail(5))

        # ✅ Safe plotting
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=prices, mode='lines', name=ticker))
            fig.update_layout(
                title=f"{ticker} Historical Closing Prices",
                xaxis_title="Days",
                yaxis_title="Price",
                hovermode="x"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Plotting error: {e}")

        # 📰 News via LLM
        with st.spinner("🌐 Fetching news..."):
            news = fetch_news_with_llm(ticker)

        st.subheader("📰 News Summary")
        st.write(news)

        # 📉 Volatility
        with st.spinner("📉 Calculating volatility..."):
            vol_series = calculate_volatility(prices)
            latest_vol = round(vol_series.iloc[-1], 5) if not vol_series.empty else "Unavailable"

        st.subheader("📉 Volatility Index")
        st.write(f"Latest Volatility: {latest_vol}")

        # 🤖 AI Response
        with st.spinner("🧠 Analyzing with LLM..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=str(prices.tail(30).tolist()),
                volatility_info=f"{latest_vol}",
                news_summary=news
            )

        st.subheader("🧠 AI Advice")
        st.markdown(response)
