from langgraph.graph import StateGraph
from app.chat.agent.states.global_state import GlobalState
from app.chat.agent.agents.caption_agent import generate_caption
from app.chat.agent.tools.instagram import post_to_instagram

async def build_post_graph():

    builder = StateGraph(GlobalState)

    async def generate(state: GlobalState):
        caption = await generate_caption(
            topic="cricket",
            tone="funny",
            platform="instagram"
        )
        state.response = caption
        return state

    async def approval(state: GlobalState):
        state.response += "\n\nReply APPROVE to post."
        return state

    async def execute(state: GlobalState):
        result = post_to_instagram(state.response)
        state.response = f"✅ Posted successfully: {result}"
        return state

    builder.add_node("generate", generate)
    builder.add_node("approval", approval)
    builder.add_node("execute", execute)

    builder.set_entry_point("generate")
    builder.add_edge("generate", "approval")

    return builder.compile()