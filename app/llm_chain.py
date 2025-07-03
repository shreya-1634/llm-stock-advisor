from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st

llm = ChatOpenAI(
    temperature=0.3,
    model="gpt-4",
    api_key=st.secrets["OPENAI_API_KEY"]
)

template = """
You are a financial advisor bot. Based on:

- Stock Symbol: {symbol}
- Recent Prices: {price_data}
- Volatility Index: {volatility_info}
- News Summary: {news_summary}
- Future Predictions: {future_predictions}

Give a clear investment recommendation (BUY, SELL, or HOLD) with reasoning.
"""

prompt = PromptTemplate.from_template(template)
chain = LLMChain(llm=llm, prompt=prompt)

def get_llm_response(symbol, price_data, volatility_info, news_summary, future_predictions):
    return chain.invoke({
        "symbol": symbol,
        "price_data": price_data,
        "volatility_info": volatility_info,
        "news_summary": news_summary,
        "future_predictions": future_predictions
    })
