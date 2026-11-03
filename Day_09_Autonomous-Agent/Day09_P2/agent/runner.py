from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio

from mcp_client import (
    connect,
    disconnect,
    discover_tools
)

from planner import planner
from executor import execute_action
from loop import run_agent_loop


load_dotenv()

llm = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def format_answer(state):

    results = "\n".join(
        f"- {o['action']}: {o['observation']}"
        for o in state["observations"]
        if not str(o["observation"]).startswith("Skipped")
    ) or "No results."

    prompt = f"""
The user asked:

{state["user_request"]}

Results:

{results}

Answer the user naturally.

Rules:
- Use ONLY the results above for facts. Never guess.
- Show every value (password, time, dice number) exactly as given.
- If a part of the request has no result, say it could not be done.
- Do not mention planning, state or tools.
"""

    response = llm.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()


async def main():

    mcp_client = await connect()

    tools = await discover_tools(mcp_client)

    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)

    user_request = input("\nUser : ")

    state = await run_agent_loop(
        user_request,
        planner,
        execute_action,
        format_answer,
        tools,
        mcp_client
    )

    print()
    print("Final Answer:")
    print(state["final_answer"])

    await disconnect(mcp_client)


if __name__ == "__main__":
    asyncio.run(main())