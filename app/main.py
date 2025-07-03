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
        st.success(f"✅ Loaded {len(prices)} daily prices.")

        # Show sample prices
        st.write("📊 Sample closing prices:", prices.tail(5))

        # ✅ Convert to list for plotting
        price_list = prices.tolist() if hasattr(prices, "tolist") else list(prices)

        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=price_list, mode='lines', name=ticker))
            fig.update_layout(
                title=f"{ticker} Historical Closing Prices",
                xaxis_title="Days",
                yaxis_title="Price",
                hovermode="x"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Plotting error: {e}")

        # 📰 Fetch News from Web
        with st.spinner("🌐 Fetching news..."):
            news = fetch_news_with_llm(ticker)

        st.subheader("📰 News Summary")
        for para in news.split("\n\n"):
            st.markdown(f"- {para.strip()}")

        # 📉 Volatility Calculation
        with st.spinner("📉 Calculating volatility..."):
            vol_series = calculate_volatility(prices)

        st.subheader("📉 Volatility Index")
        if vol_series is not None and not vol_series.empty:
            latest_vol = round(vol_series.iloc[-1], 5)
            st.write(f"Latest Volatility: Ticker {ticker.upper()}, {latest_vol}")
        else:
            st.warning("⚠️ Volatility could not be calculated.")

        # 🤖 AI-Based Analysis
        with st.spinner("🧠 Analyzing with LLM..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=str(price_list[-30:]),  # send last 30 values
                volatility_info=str(latest_vol if vol_series is not None else "N/A"),
                news_summary=news
            )

        st.subheader("🧠 AI Advice")
        st.markdown(response)
