from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GlobalState(BaseModel):
    user_id: str
    account_id: Optional[str] = None
    message: str
    niche: Optional[str] = "General"
    ai_tone: Optional[str] = "Analytical"
    intent: Optional[str] = None
    response: Optional[str] = None
    task_data: Dict[str, Any] = {}
    messages: Annotated[List[BaseMessage], add_messages] = []