from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def build_tool_descriptions(tools):

    descriptions = ""

    for tool in tools:

        descriptions += f"""
Tool:
{tool.name}

Description:
{tool.description}

----------------------------
"""

    return descriptions


def clean_action(reply, tools):

    """
    Turn the model's reply into a valid tool name or FINISH.
    """

    # Remove thinking text from models like qwen3
    if "</think>" in reply:
        reply = reply.split("</think>")[-1]

    reply = reply.strip().strip(" .`'\"\n")

    if reply.upper() == "FINISH":
        return "FINISH"

    for tool in tools:
        if tool.name in reply:
            return tool.name

    # Unknown reply -> stop safely
    return "FINISH"


def planner(state, tools):

    tool_descriptions = build_tool_descriptions(tools)

    done = state["actions"]

    not_used = [
        tool.name
        for tool in tools
        if tool.name not in done
    ]

    observations = "\n".join(
        f"- {o['action']} -> {o['observation']}"
        for o in state["observations"]
    ) or "None yet"

    prompt = f"""
You are an AI Planner.

Your job is to decide ONLY the next action.

User Request:
{state["user_request"]}

Already done:
{done if done else "Nothing yet"}

Results so far:
{observations}

Tools not used yet:
{not_used}

Available Tools:
{tool_descriptions}

Rules:

1. Split the user request into parts.
2. Check each part against "Already done".
3. Choose ONE tool for a part that is NOT done yet.
4. Never choose a tool from "Already done".
5. If every part of the request is done, return FINISH.
6. Return ONLY the tool name or FINISH. No explanation.

Next Action:
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are an AI planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    reply = response.choices[0].message.content

    return clean_action(reply, tools)