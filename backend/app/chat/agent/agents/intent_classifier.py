from openai import OpenAI
from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv
from pydantic import Field, BaseModel
from typing import Literal

load_dotenv()


class Intent(BaseModel):
    Intent: Literal["CHAT", "POST", "ANALYTICS", "SCHEDULE"] = Field(..., description="The intent of the message")

llm=ChatOpenAI()

Intent_llm=llm.with_structured_output(Intent)

def classify_intent(message: str) -> str:
    prompt = f"""
    Classify intent:
    CHAT
    POST
    ANALYTICS
    SCHEDULE

    Message: {message}
    """

    response = Intent_llm.invoke(prompt)

    return response.Intent