# app/chat/services/agent_service.py
from langgraph.graph import StateGraph, END
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from ...core.config import settings
from contextlib import asynccontextmanager, AsyncExitStack

def get_psycopg_conn_string(sqlalchemy_url: str) -> str:
    from urllib.parse import urlparse
    url = urlparse(sqlalchemy_url)
    return (
        f"user={url.username} "
        f"password={url.password} "
        f"host={url.hostname} "
        f"port={url.port} "
        f"dbname={url.path.lstrip('/')}"
    )

psycopg_conn_string = get_psycopg_conn_string(settings.DATABASE_URL)

llm = ChatOpenAI(model="gpt-5")

def chat_node(state: dict):
    # response = llm.invoke(state["messages"])
    response = "Hi i am zeeshan."
    return {"messages": state["messages"] + [response]}

graph = StateGraph(dict)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up: Initializing agent with PostgreSQL checkpointer...")
    
    # Create exit stack to manage context managers
    exit_stack = AsyncExitStack()
    
    try:
        # Create and enter PostgreSQL checkpointer context
        
        checkpointer = await exit_stack.enter_async_context(
            AsyncPostgresSaver.from_conn_string(psycopg_conn_string)
            
        )
        await checkpointer.setup()
        print("PostgreSQL checkpointer connection established.")
        
        # Compile graph with checkpointer
        app.state.graph = graph.compile(checkpointer=checkpointer)
        app.state.checkpointer = checkpointer
        app.state.exit_stack = exit_stack  # Store for cleanup
        
        print("Agent initialized successfully.")
        
        yield
        
    finally:
        # Shutdown
        print("Shutting down: Cleaning up resources...")
        await exit_stack.aclose()
        print("Resources cleaned up.")