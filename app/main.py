import streamlit as st
import os
import plotly.graph_objects as go
from app.utils import (
    fetch_all_prices,
    fetch_news_with_links,
    calculate_volatility,
    predict_future_prices,
    generate_ai_advice
)

# Read OpenAI key securely
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="LLM Stock Advisor", layout="wide")
st.title("📈 LLM-Powered Stock Market Advisor")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS):", value="AAPL")

if ticker:
    with st.spinner("Fetching stock data..."):
        prices = fetch_all_prices(ticker)
        df = prices  # Already a DataFrame

    if df is None or df.empty:
        st.warning("⚠️ Failed to fetch stock prices. Please check the ticker symbol.")
    else:
        df.index = df.index.tz_localize(None)

        # --- 📊 Chart Section ---
        st.subheader("📊 Stock Price Chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Price"],
            mode="lines",
            name="Price",
            line=dict(color="royalblue")
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=True,
            template="plotly_white",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- 📰 News Section ---
        st.subheader("📰 Recent News Headlines")
        with st.spinner("Fetching news..."):
            headlines = fetch_news_with_links(ticker)
        if headlines:
            for item in headlines:
                st.markdown(f"- [{item['title']}]({item['url']})")
        else:
            st.warning("⚠️ Could not fetch news at the moment.")

        # --- 📈 Volatility ---
        st.subheader("📉 Market Volatility")
        volatility = calculate_volatility(df["Price"])
        st.write(f"**Volatility (Std Dev):** {volatility:.2f}")

        # --- 🔮 Future Prediction ---
        st.subheader("🔮 Future Price Prediction")
        future = predict_future_prices(df)
        if future is not None:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=future.index,
                y=future,
                mode="lines+markers",
                name="Predicted",
                line=dict(color="green")
            ))
            fig2.update_layout(
                xaxis_title="Date",
                yaxis_title="Predicted Price (USD)",
                template="plotly_white"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # --- 🤖 AI Advice ---
        st.subheader("🤖 AI Investment Advice")
        with st.spinner("Analysing..."):
            ai_opinion = generate_ai_advice(ticker, df, headlines, volatility)
        st.info(f"💡 **AI Suggests:** `{ai_opinion}`")

        # --- ✅ Permission Request ---
        st.subheader("🔐 Automated Action")
        st.write(f"Based on current analysis, AI suggests to **{ai_opinion}** the stock **{ticker}**.")

        confirm = st.checkbox("✅ Allow AI to perform this action on my behalf")

        if confirm:
            st.success(f"✅ AI is authorized to {ai_opinion} {ticker} (simulated).")
        else:
            st.warning("⚠️ AI is not authorized to take action. Waiting for user permission.")
