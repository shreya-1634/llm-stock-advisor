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
        st.write("📊 Sample closing prices:", prices.tail(5))

        # ✅ Prepare data for chart
        prices.index = prices.index.astype("datetime64[ns]")  # ensure datetime x-axis
        price_df = prices.reset_index()
        price_df.columns = ["Date", "Close"]

        # 📈 Interactive Google-Finance-style chart
        try:
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
                        buttons=list([
                            dict(count=1, label="1D", step="day", stepmode="backward"),
                            dict(count=7, label="1W", step="day", stepmode="backward"),
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Plotting error: {e}")

        # 📰 News
        with st.spinner("🌐 Fetching news..."):
            news = fetch_news_with_llm(ticker)

        st.subheader("📰 News Summary")
        for para in news.split("\n\n"):
            st.markdown(f"- {para.strip()}")

        # 📉 Volatility
        with st.spinner("📉 Calculating volatility..."):
            vol_series = calculate_volatility(prices)

        st.subheader("📉 Volatility Index")
        if vol_series is not None and not vol_series.empty:
            latest_vol = round(vol_series.iloc[-1], 5)
            st.write(f"Latest Volatility: Ticker {ticker.upper()}, {latest_vol}")
        else:
            st.warning("⚠️ Volatility could not be calculated.")

        # 🤖 LLM Advice
        with st.spinner("🧠 Analyzing with LLM..."):
            response = get_llm_response(
                symbol=ticker,
                price_data=str(price_df["Close"].tail(30).tolist()),
                volatility_info=str(latest_vol if vol_series is not None else "N/A"),
                news_summary=news
            )

        st.subheader("🧠 AI Advice")
        st.markdown(response)
