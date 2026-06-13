
import sys
import os
import asyncio
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def test():
    try:
        from app.chat.services.agent_service import mcp_client
        tools = await mcp_client.get_tools()
        print(f"Tools available: {[t.name for t in tools]}")
        if tools:
            tool = tools[0]
            print(f"Tool type: {type(tool)}")
            print(f"Tool methods: {dir(tool)}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
