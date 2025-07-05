from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

template = """
Given the stock symbol {symbol}, current price data, market volatility of {volatility:.2f}%, and recent news headlines:
{news}

What is your analysis of this stock's trend?
Should the user BUY, SELL, or HOLD? Explain briefly.
"""

prompt = PromptTemplate(
    input_variables=["symbol", "volatility", "news"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

def get_llm_response(symbol, volatility, news):
    news_text = "\n".join([f"- {title}" for title, _ in news])
    return chain.run({
        "symbol": symbol,
        "volatility": volatility,
        "news": news_text
    })
