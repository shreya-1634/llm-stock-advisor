from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from openai import OpenAIError

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

prompt = ChatPromptTemplate.from_template("""
You are a smart financial assistant.

📈 Stock Symbol: {symbol}
📊 Price Trend: {price_data}
📉 Volatility: {volatility_info}
📰 News Summary: {news_summary}

Analyze the data and provide:
1. Predicted Prices for Next 5 Days
2. Buy/Sell/Hold Recommendation
3. Reason

Respond in this format:
Predicted Prices: [...]
Decision: ...
Reason: ...
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
        return "⚠️ OpenAI API key issue. Please check your API key in `.streamlit/secrets.toml`."
    except Exception as e:
        return f"❌ LLM Error: {str(e)}"
