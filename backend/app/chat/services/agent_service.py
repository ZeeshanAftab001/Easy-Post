# app/whatsapp/services/agent_service.py
from typing import Dict, Any, Optional, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from ...core.config import settings
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    user_id: str
    chat_id: str
    messages: List[BaseMessage]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4
)

def chat_node(state: AgentState):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

# Create the graph
graph = StateGraph(AgentState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

# Instead, create a function to get the agent
async def get_agent():
    """Get agent with properly initialized checkpointer"""
    async with AsyncPostgresSaver.from_conn_string(settings.DATABASE_URL) as checkpointer:
        return graph.compile(checkpointer=checkpointer)

agent = graph.compile()  # No checkpointer for development