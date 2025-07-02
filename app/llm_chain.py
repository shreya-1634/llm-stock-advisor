import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

load_dotenv()

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

prompt = PromptTemplate.from_template("""
You are a financial analyst. Based on recent price data and news, predict the next 10 days,
decide whether to BUY / SELL / HOLD, and explain why.

Ticker: {ticker}
Prices: {prices}
News: {news}

Respond ONLY in this JSON format (no code blocks):
{
  "forecast": "...",
  "decision": "...",
  "explanation": "..."
}
""")

chain = prompt | llm

def get_llm_response(ticker, prices, news):
    return chain.invoke({
        "ticker": ticker,
        "prices": prices,
        "news": news
    })
