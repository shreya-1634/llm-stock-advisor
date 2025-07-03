from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from openai import OpenAIError

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

prompt = ChatPromptTemplate.from_template("""
You are a smart financial assistant.

📈 Stock Symbol: {symbol}
📊 Price Trend: {price_data}
🌪️ Volatility Info: {volatility_info}
📰 News Summary: {news_summary}

Based on this combined data, should the user **Buy**, **Sell**, or **Hold** this stock?

Respond in this format:
Decision: <Buy/Sell/Hold>
Reason: <Short Explanation>
""")

chain = prompt | llm

def get_llm_response(symbol: str, price_data: str, volatility_info: str, news_summary: str) -> str:
    try:
        return chain.invoke({
            "symbol": symbol,
            "price_data": price_data,
            "volatility_info": volatility_info,
            "news_summary": news_summary
        })
    except OpenAIError:
        return "⚠️ OpenAI Authentication Error: Please check your API key in Streamlit secrets."
    except Exception as e:
        return f"❌ Unexpected LLM error: {str(e)}"
