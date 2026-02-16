# app/chat/services/agent_service.py
from langgraph.graph import StateGraph, START, END, add_messages
from fastapi import FastAPI
from typing import TypedDict, Annotated, Literal, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, RemoveMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from ...core.config import settings
from contextlib import asynccontextmanager, AsyncExitStack
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.client import MultiServerMCPClient
import sys


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

client = MultiServerMCPClient(
    {
        "instagram": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "app.mcp.server"],
        },
    }
)

llm = ChatOpenAI(model="gpt-4")


class ChatState(TypedDict):
    summary: str
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: int


async def build_graph():
    tools = await client.get_tools()

    print("*" * 40)
    print("Fetched tools from MCP client:")
    for tool in tools:
        print(f"- {tool.name}")

    llm_with_tools = llm.bind_tools(tools)

    async def summarize_conversation(state: ChatState):
        """Summarize the conversation and keep only last 2 messages."""
        existing_summary = state.get("summary", "")

        # Build summarization prompt
        if existing_summary:
            prompt = (
                f"Existing summary:\n{existing_summary}\n\n"
                "Extend the summary using the new conversation above."
            )
        else:
            prompt = "Summarize the conversation above."

        # For summarization, only use Human and AI content messages
        messages_for_summary = []
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                messages_for_summary.append(msg)
            elif isinstance(msg, AIMessage):
                # Create a clean copy without tool_calls
                clean_msg = AIMessage(content=msg.content or "")
                messages_for_summary.append(clean_msg)

        messages_for_summary.append(HumanMessage(content=prompt))

        response = await llm.ainvoke(messages_for_summary)

        # Keep only last 2 messages verbatim
        messages_to_delete = state["messages"][:-2]

        return {
            "summary": response.content,
            "messages": [RemoveMessage(id=m.id) for m in messages_to_delete],
        }

    async def chat_node(state: ChatState):
        """Main chat node that handles conversation with tools."""
        # Build messages for LLM
        llm_messages = []

        # Add conversation summary if it exists
        summary = state.get("summary", "")
        if summary:
            llm_messages.append(SystemMessage(
                content=f"Conversation summary:\n{summary}\n\n"
                        "Use this summary to maintain context of the ongoing conversation."
            ))

        # Add system prompt
        llm_messages.append(SystemMessage(
            content=(
                "You are EasyPost AI, a social media automation assistant. "
                "You help users create, schedule, and analyze social media posts. "
                "Always be concise and actionable.\n"
                f"The user_id is {state['user_id']}."
            )
        ))

        # Build proper message sequence for OpenAI
        # This handles the tool call/response pairing correctly
        message_sequence = []

        for msg in state["messages"]:
            # Handle Human messages
            if isinstance(msg, HumanMessage):
                message_sequence.append(msg)

            # Handle AI messages with tool calls
            elif isinstance(msg, AIMessage):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Check if we have corresponding tool responses in subsequent messages
                    tool_call_ids = {tc['id'] for tc in msg.tool_calls}

                    # Look for tool responses that match these IDs
                    found_responses = []
                    remaining_messages = state["messages"][state["messages"].index(msg) + 1:]

                    for next_msg in remaining_messages:
                        if (isinstance(next_msg, ToolMessage) and
                                next_msg.tool_call_id in tool_call_ids):
                            found_responses.append(next_msg)
                            tool_call_ids.remove(next_msg.tool_call_id)

                    # If we have all responses, include the full sequence
                    if not tool_call_ids:  # All tool calls have responses
                        message_sequence.append(msg)
                        message_sequence.extend(found_responses)
                    else:
                        # Some tool calls don't have responses, create clean AI message
                        clean_msg = AIMessage(content=msg.content or "I'll help you with that.")
                        message_sequence.append(clean_msg)
                else:
                    # AI message without tool calls
                    message_sequence.append(msg)

            # Handle standalone ToolMessages (shouldn't happen, but just in case)
            elif isinstance(msg, ToolMessage):
                # This should only be reached if a ToolMessage isn't paired with an AI message
                # In this case, skip it to avoid API errors
                continue

        # Add the filtered message sequence to LLM messages
        llm_messages.extend(message_sequence)

        try:
            response = await llm_with_tools.ainvoke(llm_messages)
            return {"messages": [response]}
        except Exception as e:
            print(f"Error in chat_node: {str(e)[:200]}")
            # Fallback: use regular LLM without tools
            fallback_response = await llm.ainvoke(llm_messages)
            return {"messages": [fallback_response]}

    def should_summarize(state: ChatState) -> Literal["summarize", END]:
        """Condition to check if we should summarize the conversation."""
        # Count only Human and non-tool-call AI messages
        count = 0
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                count += 1
            elif isinstance(msg, AIMessage) and not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                count += 1

        # Summarize when we have more than 6 messages
        return "summarize" if count > 6 else END

    # Create graph
    builder = StateGraph(ChatState)

    # Add nodes
    builder.add_node("chat", chat_node)
    builder.add_node("summarize", summarize_conversation)
    builder.add_node("tools", ToolNode(tools))

    # Add edges
    builder.add_edge(START, "chat")

    # Conditional edge from chat to either summarize or end
    builder.add_conditional_edges(
        "chat",
        should_summarize,
        {
            "summarize": "summarize",
            END: END,
        }
    )

    # Add edge from summarize back to chat (so conversation continues after summarization)
    builder.add_edge("summarize", "chat")

    # Tool handling edges
    builder.add_conditional_edges("chat", tools_condition)
    builder.add_edge("tools", "chat")

    return builder


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
        graph = await build_graph()
        app.state.graph = graph.compile(checkpointer=checkpointer)
        app.state.checkpointer = checkpointer
        app.state.exit_stack = exit_stack
        print("Agent initialized successfully.")

        yield

    finally:
        # Shutdown
        print("Shutting down: Cleaning up resources...")
        await exit_stack.aclose()
        print("Resources cleaned up.")


async def show_state(graph, config: dict):
    """Display current state (for debugging)."""
    snap = await graph.aget_state(config)
    vals = snap.values
    print("\n--- STATE ---")
    print("summary:", vals.get("summary", ""))

    all_messages = vals.get("messages", [])
    print(f"total_messages: {len(all_messages)}")

    print("\nmessages:")
    for i, msg in enumerate(all_messages):
        if isinstance(msg, RemoveMessage):
            print(f"[{i}] RemoveMessage (id: {msg.id})")
        elif isinstance(msg, HumanMessage):
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            print(f"[{i}] Human: {content}")
        elif isinstance(msg, AIMessage):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"[{i}] AI (with {len(msg.tool_calls)} tool calls)")
                for tc in msg.tool_calls:
                    print(f"    - Tool call: {tc.get('function', {}).get('name', 'unknown')}")
            else:
                content = msg.content[:50] + "..." if msg.content and len(
                    msg.content) > 50 else msg.content or "No content"
                print(f"[{i}] AI: {content}")
        elif isinstance(msg, ToolMessage):
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            print(f"[{i}] Tool (call_id: {msg.tool_call_id[:8]}...): {content}")
        else:
            print(f"[{i}] {type(msg).__name__}")