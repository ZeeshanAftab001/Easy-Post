
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    print(f"Methods of MultiServerMCPClient: {dir(MultiServerMCPClient)}")
except Exception as e:
    print(f"Error: {e}")
