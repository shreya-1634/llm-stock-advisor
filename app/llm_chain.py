from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

template = """
You are a financial advisor AI. Use the news and market volatility to suggest an action for the stock {symbol}.
News: {news_summary}
Volatility: {volatility}%

Based on this, should the investor Buy, Sell, or Hold?
Reply in one short sentence.
"""

prompt = PromptTemplate.from_template(template)

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

chain = LLMChain(llm=llm, prompt=prompt)

def get_llm_response(symbol, news_summary, volatility):
    return chain.invoke({
        "symbol": symbol,
        "news_summary": news_summary,
        "volatility": volatility or 0.0,
    })
