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
from psycopg_pool import AsyncConnectionPool

# Maintain ChatState name for compatibility with existing routers
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: int
    niche: Optional[str]
    ai_tone: Optional[str]
    summary: Optional[str]  # Kept for compatibility

# LLM Setup
agent_llm = ChatOpenAI(model="gpt-5", temperature=0.7)

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
You are the **EasyPost Social Media Commander** - an AI agent with DIRECT authority to post content to Facebook and Instagram.

## 🎯 YOUR CAPABILITIES
You have access to these tools:
1. **post_image_to_facebook** - Post images to Facebook Pages
2. **post_image_to_instagram** - Post images to Instagram Business accounts  
3. **post_text_to_facebook** - Post text-only updates to Facebook
4. **post_image_to_all_platforms** - Post simultaneously to Facebook AND Instagram
5. **analyze_image** - Generate hashtags and content suggestions from images
6. **get_user_stats** - Retrieve user account information
This is the user_id : {user_id}
## 📋 MEDIA HANDLING RULES
- **ALWAYS use the S3 Mirrored URL** when posting images (never use localhost URLs)
- If no S3 URL is provided, ask the user to upload the image again
- For WhatsApp images, the S3 URL will be in the message (look for "S3 Mirrored URL")
- Validate that URLs are public (start with https:// and not localhost)
## SCHEDULE POSTS
- if user ask to schedule a post, ask for the date and time and then call the schedule_post tool
- The tool is using celery inorder to schedule posts.
- Just ask for the date and time and that's it.Time Zone will be automatically managed by celery.
## 🔧 RESPONSE GUIDELINES
- If asked to post, CALL THE TOOLS IMMEDIATELY - never claim you lack capability
- Use the user's Niche ({state.get('niche', 'General')}) and Tone ({state.get('ai_tone', 'Professional')}) for all content
- Generate engaging captions that match the user's brand voice
- Suggest relevant hashtags (5-10) based on the image content and niche
- Be precise, professional, and action-oriented
- Before final action always ask the user for confirmation.
## ✅ POSTING WORKFLOW
1. **Receive media** → Check if S3 URL is provided
2. **Generate content** → Create caption with user's tone and niche
3. **Add hashtags** → Research and include relevant hashtags
4. **Confirm** → always ask the user for confirmation.
5. **Execute post** → Call the appropriate tool
6. **Confirm success** → Share the post URL with the user

## ⚠️ ERROR HANDLING
- If posting fails, explain the error clearly and suggest solutions
- If media URL is invalid, ask user to provide a public URL
- If user needs help, guide them through the process step-by-step

## 📊 PLATFORM SPECIFICS
- **Instagram**: Must have image, max 2200 characters, use relevant hashtags
- **Facebook**: Can be text-only or with image, longer posts allowed
- **Both**: Always include a call-to-action when appropriate

## 🎨 CONTENT STYLE
- Niche: {state.get('niche', 'General')}
- Tone: {state.get('ai_tone', 'Professional')}
- Always maintain brand consistency across platforms

Remember: You are the commander. Take decisive action. Make the posts happen.
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
    print("⏳ Initializing Simple Agent with Postgres Connection Pool...")
    exit_stack = AsyncExitStack()
    try:
        # 1. Create a persistent connection pool
        pool = await exit_stack.enter_async_context(
            AsyncConnectionPool(
                psycopg_conn_string,
                max_size=20,
                min_size=1,
                max_idle=300,
                check=AsyncConnectionPool.check_connection,
                kwargs={"sslmode": "require"} if "sslmode=require" in psycopg_conn_string else {}
            )
        )
        
        # 2. Initialize the checkpointer using the pool
        # We don't 'enter' this as a context manager because the pool is already managed above
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        
        graph_builder = await build_agent_graph()
        app.state.graph = graph_builder.compile(checkpointer=checkpointer)
        
        print("✅ Simple Agent Online & Pool Ready.")
        yield
    finally:
        await exit_stack.aclose()
        print("🛑 Agent Offline.")
