import asyncio
from fastmcp import Client
from server import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print([tool.name for tool in tools])

        result = await client.call_tool("roll_dice", {})
        print("Dice Result:", result.content[0].text)


asyncio.run(main())