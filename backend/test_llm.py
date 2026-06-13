
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

async def test_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Testing OpenAI with key: {api_key[:10]}...")
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
    try:
        resp = await llm.ainvoke([HumanMessage(content="Hi")])
        print(f"Success: {resp.content}")
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
