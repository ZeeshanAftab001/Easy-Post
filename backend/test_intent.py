
import asyncio
from app.chat.agent.agents.intent_classifier import classify_intent

def test():
    msg1 = "can you help me post a photo on facebook?"
    intent1 = classify_intent(msg1)
    print(f"Message: {msg1} -> Intent: {intent1}")

    msg2 = "How can I improve my Instagram reach?"
    intent2 = classify_intent(msg2)
    print(f"Message: {msg2} -> Intent: {intent2}")

if __name__ == "__main__":
    test()
