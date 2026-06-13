from langgraph.graph import StateGraph
from app.chat.agent.states.global_state import GlobalState
from app.chat.agent.tools.analytics import fetch_instagram_analytics

async def build_analytics_graph():

    builder = StateGraph(GlobalState)

    async def analytics(state: GlobalState):
        data = fetch_instagram_analytics(state.account_id)
        state.response = str(data)
        return state

    builder.add_node("analytics", analytics)
    builder.set_entry_point("analytics")

    return builder.compile()