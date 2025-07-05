import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils import (
    fetch_all_prices,
    fetch_news_with_links,
    calculate_volatility,
    predict_future_prices,
)
from llm_chain import get_llm_response

import plotly.graph_objects as go
import datetime

# Load API key
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="LLM Stock Advisor", layout="wide")
st.title("📈 LLM Stock Advisor")

ticker = st.text_input("Enter stock ticker (e.g., AAPL, RELIANCE.NS):", value="AAPL")

if ticker:
    prices = fetch_all_prices(ticker)
    if prices is not None:
        # Prepare DataFrame
        df = prices.to_frame(name="Price")
        df["Date"] = df.index

        # Plot interactive chart like Google Finance
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Price"],
            mode="lines",
            name=ticker,
            line=dict(color="royalblue")
        ))

        fig.update_layout(
            title=f"{ticker} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis=dict(rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
                rangeslider=dict(visible=True),
                type="date"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # 📉 Volatility
        volatility = calculate_volatility(prices)
        st.markdown(f"📊 **Market Volatility**: `{volatility:.2f}%`")

        # 📰 News
        st.subheader("📰 Recent News")
        news = fetch_news_with_links(ticker)
        if news:
            for item in news:
                st.markdown(f"- [{item['title']}]({item['url']})")
        else:
            st.warning("No news found.")

        # 🔮 Future Prices
        future = predict_future_prices(prices)
        if future is not None:
            st.subheader("🔮 Predicted Future Prices")
            st.line_chart(future)

        # 🤖 AI Suggestion
        st.subheader("🤖 AI Investment Advice")
        advice = generate_ai_advice(ticker, prices, news)
        st.markdown(f"**AI Suggestion:** `{advice}`")

        # ✅ User Permission
        if st.toggle("Allow AI to act on suggestion?"):
            st.success(f"✅ AI has permission to: **{advice}**")
        else:
            st.info("❗ AI is waiting for permission to act.")

    else:
        st.warning("⚠️ Failed to fetch stock prices. Check the ticker.")
