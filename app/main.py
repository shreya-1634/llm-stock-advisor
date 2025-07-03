import streamlit as st
import plotly.graph_objects as go
from utils import (
    fetch_all_prices,
    fetch_news_with_llm,
    calculate_volatility,
    predict_future_prices,
    fetch_market_volatility
)
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="centered")
st.title("🤖 LLM-Powered Stock Advisor")

# ─────────────────────
# 🔐 LOGIN SYSTEM (simulated)
# ─────────────────────
st.sidebar.title("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

is_logged_in = username == "demo" and password == "1234"

# ─────────────────────
# 📉 Market Volatility Index
# ─────────────────────
vix = fetch_market_volatility()
st.sidebar.header("📉 Market Volatility")
if vix:
    st.sidebar.metric(label="India VIX", value=vix)
else:
    st.sidebar.warning("Couldn't load VIX index.")

# ─────────────────────
# ✅ IF LOGGED IN: Show App
# ─────────────────────
if not is_logged_in:
    st.warning("Please login to use the advisor.")
else:
    ticker = st.text_input("🔍 Enter stock ticker (e.g., AAPL, INFY.NS)", value="AAPL")

    if st.button("📊 Analyze"):
        with st.spinner("📥 Fetching stock price history..."):
            prices = fetch_all_prices(ticker)

        if prices is None or prices.empty:
            st.warning("⚠️ Could not retrieve stock data. Check the ticker symbol.")
        else:
            st.success(f"✅ Loaded {len(prices)} daily prices.")

            prices.index = prices.index.astype("datetime64[ns]")
            price_df = prices.reset_index()
            price_df.columns = ["Date", "Close"]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=price_df["Date"],
                y=price_df["Close"],
                mode='lines',
                name=ticker.upper(),
                line=dict(color='deepskyblue')
            ))
            fig.update_layout(
                title=f"{ticker.upper()} Historical Prices",
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

            with st.spinner("🌐 Fetching news..."):
                news = fetch_news_with_llm(ticker)

            st.subheader("📰 News Summary")
            st.markdown(news or "No recent news available.")

            with st.spinner("📉 Calculating volatility..."):
                vol_series = calculate_volatility(prices)

            st.subheader("📉 Volatility Index")
            if vol_series is not None and not vol_series.empty:
                latest_vol = round(vol_series.iloc[-1], 5)
                st.write(f"Latest Volatility: {latest_vol}")
            else:
                st.warning("⚠️ Could not calculate volatility.")

            with st.spinner("🔮 Predicting future prices..."):
                future_prices = predict_future_prices(prices)
                st.subheader("🔮 Next 5-Day Forecast")
                for i, price in enumerate(future_prices, 1):
                    st.markdown(f"Day {i}: **₹{price:.2f}**")

            with st.spinner("🧠 AI-Powered Advice..."):
                response = get_llm_response(
                    symbol=ticker,
                    price_data=str(price_df["Close"].tail(30).tolist()),
                    volatility_info=str(latest_vol if vol_series is not None else "N/A"),
                    news_summary=news,
                    future_predictions=str(future_prices.tolist())
                )

            st.subheader("🧠 AI Advice")
            st.markdown(response)

            st.subheader("📩 AI Trading Confirmation")
            if st.checkbox("✅ Allow AI to take action on this?"):
                action = response.lower()
                if "buy" in action:
                    st.success("📈 Placing a simulated BUY order...")
                elif "sell" in action:
                    st.error("📉 Placing a simulated SELL order...")
                elif "hold" in action:
                    st.info("🟡 Holding position as advised.")
                else:
                    st.warning("⚠️ AI couldn’t determine an exact action.")
            else:
                st.info("Awaiting your confirmation to proceed.")
