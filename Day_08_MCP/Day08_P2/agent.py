import asyncio

from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

from mcp_client import (
    connect,
    disconnect,
    discover_tools,
    execute_tool
)



async def main():
# Step 1: Connect to the MCP Server.
    client = await connect()

    # Step 2: Discover all available tools.
    tools = await discover_tools(
        client
    )
    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)
    print() 

    
    await disconnect(
        client
    )

if __name__ == "__main__":

    asyncio.run(main())