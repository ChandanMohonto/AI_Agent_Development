import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def decompose_task(user_request):

    prompt = f"""
You are an AI task planner.

Break the user's request into smaller tasks.

Rules:

1. Create only necessary tasks.
2. Put tasks in execution order.
3. Each task should be a short action.
4. Return one task per line.
5. Do not number the tasks.
6. Do not explain anything.

User Request:

{user_request}
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,  # FIX: more consistent plans
        messages=[
            {
                "role": "system",
                "content": "You are an AI task planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    # FIX: remove thinking text from models like qwen3
    if "</think>" in result:
        result = result.split("</think>")[-1]

    tasks = []

    for line in result.splitlines():

        # FIX: remove bullets / numbers the model may add anyway
        line = line.strip().lstrip("-*•").strip()
        line = re.sub(r"^\d+[.)]\s*", "", line)

        if line:
            tasks.append(line)

    return tasks