# app/chat/services/agent_service.py
"""
Optimized Simple Social Media Agent
Direct execution, robust memory, and stable lifecycle management.
"""

from __future__ import annotations
import asyncio
import sys
import json
from typing import TypedDict, Annotated, Optional, List
from contextlib import asynccontextmanager, AsyncExitStack

from fastapi import FastAPI
from langchain_core.messages import (
    BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
)
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from ...core.config import settings
from .memory_service import store_agent_memory

# Maintain ChatState name for compatibility with existing routers
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: int
    niche: Optional[str]
    ai_tone: Optional[str]
    summary: Optional[str]  # Kept for compatibility

# LLM Setup
agent_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Database Connection Fix
def _get_psycopg_conn_string(sqlalchemy_url: str) -> str:
    url = sqlalchemy_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")
    return url.replace("ssl=require", "sslmode=require")

psycopg_conn_string = _get_psycopg_conn_string(settings.DATABASE_URL)

# MCP Client
mcp_client = MultiServerMCPClient({
    "social_media": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "app.mcp.server"],
        "env": {**__import__('os').environ, "PYTHONPATH": __import__('os').getcwd()},
    },
})

async def get_tools():
    try:
        return await mcp_client.get_tools()
    except Exception as e:
        print(f"⚠️ MCP Tool Loading Failed: {e}")
        return []

# ── Agent Logic ─────────────────────────────────────────────────────────────

async def agent_node(state: ChatState) -> dict:
    """The brain of the agent. Processes history and decides next steps."""
    
    tools = await get_tools()
    
    system_prompt = f"""
You are the **EasyPost Social Media Commander**.
You have DIRECT authority to post content using your tools.

🎯 CAPABILITIES:
- Post images/text to Facebook and Instagram.
- Generate high-engagement captions and hashtags.
- Analyze social media intent.

📋 RULES:
- If asked to post, CALL THE TOOLS IMMEDIATELY.
- Never claim you lack the capability.
- Use the user's Niche ({state.get('niche', 'General')}) and Tone ({state.get('ai_tone', 'Professional')}) for all content.
- Be precise and professional.
"""
    
    # We pass the ENTIRE message history so the agent remembers what it just did
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    llm_with_tools = agent_llm.bind_tools(tools)
    response = await llm_with_tools.ainvoke(messages)
    
    return {"messages": [response]}

async def tool_node(state: ChatState) -> dict:
    """Executes the actual platform actions."""
    last_message = state["messages"][-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": []}
    
    tools = await get_tools()
    tools_by_name = {t.name: t for t in tools}
    
    results = []
    for tool_call in last_message.tool_calls:
        t_name = tool_call["name"]
        t_args = tool_call["args"]
        print(f"🛠️  Executing Tool: {t_name}")
        
        if t_name in tools_by_name:
            try:
                res = await tools_by_name[t_name].ainvoke(t_args)
                results.append(ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=json.dumps(res) if isinstance(res, dict) else str(res)
                ))
            except Exception as e:
                results.append(ToolMessage(tool_call_id=tool_call["id"], content=f"Error: {e}"))
        else:
            results.append(ToolMessage(tool_call_id=tool_call["id"], content=f"Tool {t_name} not found"))
            
    return {"messages": results}

def should_continue(state: ChatState):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return "tools"
    return END

# ── Lifecycle & Graph ────────────────────────────────────────────────────────

async def build_agent_graph():
    builder = StateGraph(ChatState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")
    
    return builder

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Initializing Simple Agent with Postgres persistence...")
    exit_stack = AsyncExitStack()
    try:
        # Proper checkpointer lifecycle management
        checkpointer = await exit_stack.enter_async_context(
            AsyncPostgresSaver.from_conn_string(psycopg_conn_string)
        )
        await checkpointer.setup()
        
        graph_builder = await build_agent_graph()
        app.state.graph = graph_builder.compile(checkpointer=checkpointer)
        
        print("✅ Simple Agent Online & Ready to Post.")
        yield
    finally:
        await exit_stack.aclose()
        print("🛑 Agent Offline.")