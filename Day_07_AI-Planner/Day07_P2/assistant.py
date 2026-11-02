from openai import OpenAI
from dotenv import load_dotenv
import os

from planner import choose_tool

from tools import (
    get_current_time,
    roll_dice,
    generate_password
)

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

# Tool name -> Python function
TOOLS = {
    "get_current_time": get_current_time,
    "roll_dice": roll_dice,
    "generate_password": generate_password
}

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

while True:

    user_input = input("\nYou : ")

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    # 1. PLAN - AI chooses the tool
    tool = choose_tool(user_input)

    print("DEBUG tool =", tool)   # delete this line when everything works

    # 2. ACT - Python runs the tool
    if tool in TOOLS:
        result = TOOLS[tool]()
    else:
        result = None

    # Password: print exactly, so the AI can't re-type it wrongly
    if tool == "generate_password":
        print("\nAI : Here is your secure password:", result)
        continue

    # 3. RESPOND - AI writes the final answer
    if result is not None:
        prompt = f"""
The user asked:
{user_input}

The tool returned:
{result}

Answer the user naturally using only the tool result.
Do not add any extra information.
If the tool result does not answer the question,
say you can't answer that.
"""
    else:
        prompt = user_input

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    # Remove qwen3 thinking text if present
    if "</think>" in answer:
        answer = answer.split("</think>")[-1].strip()

    print("\nAI :", answer)