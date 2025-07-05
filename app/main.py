import streamlit as st
import plotly.graph_objects as go
from utils import fetch_all_prices, fetch_news_with_links, calculate_volatility, predict_future_prices
from llm_chain import get_llm_response

st.set_page_config(layout="wide")
st.title("📈 LLM Stock Advisor")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS):", value="AAPL")

if ticker:
    prices = fetch_all_prices(ticker)

    if prices is not None:
        df = prices.to_frame().rename(columns={"Close": "Price"})

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Price"], mode="lines", name="Price"))
        fig.update_layout(title=f"{ticker} Stock Price", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=True)
        st.plotly_chart(fig, use_container_width=True)

        # Volatility
        volatility = calculate_volatility(prices)
        st.metric("📉 Market Volatility", f"{volatility:.2f} %")

        # News
        news = fetch_news_with_links(ticker)
        if news:
            st.subheader("📰 Recent News")
            for title, url in news:
                st.markdown(f"- [{title}]({url})")

        # AI Prediction
        future = predict_future_prices(prices)
        if future is not None:
            st.subheader("🔮 Future Price Prediction (Next 7 Days)")
            st.line_chart(future)

        # AI Recommendation
        st.subheader("🤖 AI Advice")
        with st.spinner("Analyzing..."):
            advice = get_llm_response(ticker, volatility, news)
            st.write(advice)

        # User Permission
        st.subheader("🔐 AI Trading Permission")
        decision = st.radio("Allow AI to execute trade based on this advice?", ["No", "Yes"])
        if decision == "Yes":
            st.success(f"✅ AI is executing your trade: {advice.split()[-1].upper()} order placed!")
        else:
            st.info("❗AI will not perform any trading action.")

    else:
        st.error("⚠️ Failed to fetch data. Please check the ticker.")
