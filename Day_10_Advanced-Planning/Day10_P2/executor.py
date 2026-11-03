from mcp_client import execute_tool


async def execute_action(
    action,
    state,
    client
):

    # FIX: some tasks need no tool (e.g. "Explain Python").
    # The answer generator will handle them from general knowledge.
    if action.lower() == "none":
        return "No tool needed. Answer this task from general knowledge."

    # FIX: a wrong tool name must not crash the agent
    try:

        result = await execute_tool(
            client,
            action
        )

    except Exception as error:

        return f"Error: {error}"

    if hasattr(result, "content"):

        if result.content:
            return result.content[0].text

    return str(result)