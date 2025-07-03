import streamlit as st
import plotly.graph_objects as go
from utils import fetch_all_prices, fetch_news_with_llm, calculate_volatility
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="centered")
st.title("🤖 LLM-Powered Stock Advisor")

ticker = st.text_input("🔍 Enter stock ticker (e.g., AAPL, TCS.NS)", value="AAPL")

if st.button("📊 Analyze"):
    # 1. Fetch stock data
    with st.spinner("📥 Fetching stock price history..."):
        prices = fetch_all_prices(ticker)

    if prices is None or prices.empty:
        st.warning("⚠️ Could not retrieve stock data. Check the ticker symbol.")
    else:
        st.success(f"✅ Loaded {len(prices)} daily prices.")
        st.write("📊 Sample closing prices:", prices.tail(5))

        # 2. Prepare chart data
        prices.index = prices.index.astype("datetime64[ns]")
        price_df = prices.reset_index()
        price_df.columns = ["Date", "Close"]

        # 3. Plot interactive chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=price_df["Date"],
            y=price_df["Close"],
            mode='lines',
            name=ticker.upper(),
            line=dict(color='deepskyblue')
        ))
        fig.update_layout(
            title=f"{ticker.upper()} Historical Stock Prices",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified",
            xaxis=dict(
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(step="all")
                    ]
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 4. Fetch news
        with st.spinner("🌐 Fetching news..."):
            news = fetch_news_with_llm(ticker)

        st.subheader("📰 News Summary")
        st.markdown(news or "No recent news available.")

        # 5. Volatility
        with st.spinner("📉 Calculating volatility..."):
            vol_series = calculate_volatility(prices)

        st.subheader("📉 Volatility Index")
        if vol_series is not None and not vol_series.empty:
            latest_vol = round(vol_series.iloc[-1], 5)
            st.write(f"Latest Volatility: {latest_vol}")
        else:
            st.warning("⚠️ Volatility could not be calculated.")

        # 6. AI Advice
        with st.spinner("🧠 Analyzing with LLM..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=str(price_df["Close"].tail(30).tolist()),
                volatility_info=str(latest_vol if vol_series is not None else "N/A"),
                news_summary=news
            )

        st.subheader("🧠 AI-Powered Advice")
        st.markdown(response)
