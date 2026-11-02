from fastmcp import Client

from server import mcp


async def connect():

    """
    Connect to the MCP Server (in-memory).
    """

    client = Client(mcp)

    await client.__aenter__()

    print("Connected to MCP Server.")

    return client


async def disconnect(client):

    """
    Close the MCP connection.
    """

    await client.__aexit__(None, None, None)


async def discover_tools(client):

    """
    Retrieve all tools from the server.
    """

    return await client.list_tools()


async def execute_tool(client, tool_name, arguments=None):

    """
    Execute a tool.
    """

    if arguments is None:
        arguments = {}

    return await client.call_tool(tool_name, arguments)