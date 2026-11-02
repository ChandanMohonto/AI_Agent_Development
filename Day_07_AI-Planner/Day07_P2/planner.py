from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

TOOL_NAMES = [
    "get_current_time",
    "roll_dice",
    "generate_password"
]


def clean_tool_name(reply):
    """Clean the model's reply and return a valid tool name or 'none'."""

    # Remove qwen3 thinking text: <think> ... </think>
    if "</think>" in reply:
        reply = reply.split("</think>")[-1]

    # Lower-case and remove spaces, dots, quotes, backticks
    reply = reply.lower().strip(" .`'\"\n")

    # Exact match
    if reply in TOOL_NAMES:
        return reply

    # Model added extra words, e.g. "Tool: get_current_time"
    for name in TOOL_NAMES:
        if name in reply:
            return name

    return "none"


def choose_tool(user_request):

    planner_prompt = f"""
You are an AI planner.

Available tools:

1. get_current_time
   Use when the user asks for the current date, day or time.

2. roll_dice
   Use when the user asks to roll a dice.

3. generate_password
   Use when the user wants a secure password.

If no tool is required, return:

none

Return ONLY the tool name.

User Request:

{user_request}
"""

    response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[
            {
                "role": "system",
                "content": "You are an AI planner."
            },
            {
                "role": "user",
                "content": planner_prompt
            }
        ]
    )

    reply = response.choices[0].message.content

    return clean_tool_name(reply)