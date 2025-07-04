from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

template = """
You are a financial advisor AI. Analyze the following:

Stock: {symbol}
Recent Closing Prices: {prices}
News Headlines: {news_summary}
Volatility Index: {volatility}

Based on the price trend, news sentiment, and market volatility, suggest whether to BUY, HOLD, or SELL this stock.
Give a brief reason for your recommendation.

AI Decision:
"""

prompt = PromptTemplate(
    input_variables=["symbol", "prices", "news_summary", "volatility"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

def get_llm_response(symbol, prices, news_summary, volatility):
    return chain.invoke({
        "symbol": symbol,
        "prices": prices,
        "news_summary": news_summary,
        "volatility": volatility,
    })
