# app/llm_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

# Initialize the OpenAI LLM
llm = ChatOpenAI(temperature=0.3, model="gpt-4")

# Define structured prompt template
prompt = ChatPromptTemplate.from_template(
    """
You are an expert financial advisor AI. Analyze the following stock information:

📈 Stock Symbol: {symbol}
📊 Price Trend: {price_data}
🌪️ Volatility Info: {volatility_info}
📰 News Summary: {news_summary}

Based on this combined data, should the user BUY, SELL, or HOLD this stock?
Please provide a short, human-understandable explanation.

Respond in the format:
Decision: <Buy/Sell/Hold>
Reason: <Explanation>
"""
)

# Create the LLM chain
chain = prompt | llm

# Function to call from Streamlit
def get_llm_response(symbol: str, price_data: str, volatility_info: str, news_summary: str) -> str:
    return chain.invoke({
        "symbol": symbol,
        "price_data": price_data,
        "volatility_info": volatility_info,
        "news_summary": news_summary
    })
