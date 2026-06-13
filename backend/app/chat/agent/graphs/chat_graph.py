from langgraph.graph import StateGraph
from app.chat.agent.states.global_state import GlobalState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

async def build_chat_graph():

    builder = StateGraph(GlobalState)

    async def chat_reply(state: GlobalState):
        llm = ChatOpenAI(model="gpt-4o-mini") # Or your preferred model
        
        system_prompt = (
            "You are the Easy-Post AI Social Media Expert. "
            "Your goal is to help users manage their social media presence effectively. "
            f"The user's niche is: {state.niche}. "
            f"Maintain an AI Tone that is: {state.ai_tone}. "
            "Answer questions about strategy, hashtag research, content ideas, and general social media management. "
            "Be professional, concise, and helpful."
        )
        
        # Prepare messages
        messages = [SystemMessage(content=system_prompt)] + state.messages
        
        # Get response
        response = await llm.ainvoke(messages)
        
        # Final response is an AIMessage
        return {
            "messages": [response],
            "response": response.content
        }

    builder.add_node("chat", chat_reply)
    builder.set_entry_point("chat")

    return builder.compile()