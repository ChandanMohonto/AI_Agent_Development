import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def format_answer(state):

    prompt = f"""
The user asked:

{state["user_request"]}

Relevant previous memories:
{state["memories"]}

Tasks:
{state["tasks"]}

Actions:
{state["actions"]}

Observations:
{state["observations"]}

Intermediate Results:
{state["results"]}

Give the user a natural and concise answer.
Use relevant previous memories
when they help answer the user's question.

Rules:
- Use the observations as facts. Never invent times, numbers or passwords.
- Show every value (time, password, dice number) exactly as given.
- For a task whose observation says "No tool needed",
  answer it briefly from your own knowledge.
- If a task failed, say it could not be done.
- Only use a memory if it is clearly about this user's question.


Do not mention:
- planner
- agent loop
- MCP
- internal state
- tools
- internal reasoning
"""

    response = client.chat.completions.create(
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
