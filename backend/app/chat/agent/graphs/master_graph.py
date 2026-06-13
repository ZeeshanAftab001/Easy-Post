from langgraph.graph import StateGraph
from app.chat.agent.states.global_state import GlobalState
from app.chat.agent.agents.intent_classifier import classify_intent
from app.chat.agent.graphs.post_graph import build_post_graph
from app.chat.agent.graphs.analytics_graph import build_analytics_graph
from app.chat.agent.graphs.chat_graph import build_chat_graph

from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy import create_engine
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
memory = PostgresSaver(engine)


async def build_master_graph():

    post_graph = await build_post_graph()
    chat_graph = await build_chat_graph()
    analytics_graph =await build_analytics_graph()

    builder = StateGraph(GlobalState)

    def router(state: GlobalState):
        state.intent = classify_intent(state.message)
        return state.intent

    builder.add_conditional_edges(
        "router",
        router,
        {
            "POST": post_graph,
            "CHAT": chat_graph,
            "ANALYTICS": analytics_graph,
        }
    )

    builder.set_entry_point("router")

    return builder.compile()