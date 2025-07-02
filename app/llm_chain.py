# app/llm_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from openai import OpenAIError

# Load the model
llm = ChatOpenAI(
    temperature=0.3,
    model="gpt-4"  # or "gpt-3.5-turbo" if you're on a free tier
)

# Define structured prompt template
prompt = ChatPromptTemplate.from_template(
    """
You are a smart financial assistant.

📈 Stock Symbol: {symbol}
📊 Price Trend: {price_data}
🌪️ Volatility Info: {volatility_info}
📰 News Summary: {news_summary}

Based on this combined data, should the user **Buy**, **Sell**, or **Hold** this stock?

Respond in this format:
Decision: <Buy/Sell/Hold>
Reason: <Short Explanation>
"""
)

# Create chain
chain = prompt | llm  # RunnableSequence

def get_llm_response(symbol: str, price_data: str, volatility_info: str, news_summary: str) -> str:
    """Safely run the LLM chain and return prediction or error message."""
    try:
        return chain.invoke({
            "symbol": symbol,
            "price_data": price_data,
            "volatility_info": volatility_info,
            "news_summary": news_summary
        })
    except OpenAIError as e:
        return "⚠️ OpenAI Authentication Error: Please check your API key in Streamlit secrets."
    except Exception as e:
        return f"❌ Unexpected error from LLM: {str(e)}"
