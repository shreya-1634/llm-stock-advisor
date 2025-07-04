import streamlit as st
import plotly.graph_objects as go
from utils import (
    fetch_all_prices,
    fetch_news_with_llm,
    calculate_volatility,
    predict_future_prices
)
from llm_chain import get_llm_response

st.set_page_config(page_title="📈 LLM Stock Advisor", layout="wide")

st.title("📊 LLM Stock Advisor")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS):", "AAPL")

if st.button("Analyze"):
    with st.spinner("Fetching data..."):
        df = fetch_all_prices(ticker)
        news = fetch_news_with_llm(ticker)
        volatility = calculate_volatility(df) if df is not None else None
        future = predict_future_prices(df) if df is not None else None

    if df is None:
        st.error("⚠️ Failed to fetch stock prices.")
    else:
        # ✅ Plot Google Finance–like interactive chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            name="Closing Price",
            line=dict(color="blue", width=2)
        ))

        if future is not None:
            fig.add_trace(go.Scatter(
                x=future.index,
                y=future.values,
                name="Predicted Price",
                line=dict(color="green", dash="dash")
            ))

        fig.update_layout(
            title=f"{ticker.upper()} Stock Price Chart",
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            yaxis_title="Price (in local currency)"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ✅ Show news headlines
        st.subheader("🗞️ Latest News Headlines")
        if news:
            st.markdown(news)
        else:
            st.warning("No news found.")

        # ✅ Show volatility
        st.subheader("📉 Market Volatility")
        if volatility:
            st.markdown(f"**Annualized Volatility:** `{volatility:.2%}`")
        else:
            st.warning("Unable to calculate volatility.")

        # ✅ AI Recommendation
        st.subheader("🤖 AI Advice")
        with st.spinner("Generating advice..."):
            prices = df["Close"].tail(30).tolist()
            response = get_llm_response(
                symbol=ticker,
                prices=prices,
                news_summary=news or "No major news available.",
                volatility=f"{volatility:.4f}" if volatility else "Unknown"
            )
            st.success(response["text"])
