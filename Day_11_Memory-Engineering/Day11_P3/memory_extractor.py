import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def extract_memory(
    user_message,
    assistant_message
):
    prompt = (
        "You are a memory extraction system.\n\n"
        "Read the conversation below and determine whether\n"
        "it contains useful long-term information about the user.\n\n"
        "User:\n"
        + user_message
        + "\n\nAssistant:\n"
        + assistant_message
        + "\n\nStore information only if it will be useful\n"
        "in future conversations.\n\n"
        "Useful information includes:\n"
        "- preferences\n"
        "- interests\n"
        "- goals\n"
        "- skills\n"
        "- projects\n"
        "- important user facts\n\n"
        "Do NOT store:\n"
        "- temporary questions\n"
        "- current time\n"
        "- random calculations\n"
        "- one-time requests\n"
        "- tool results\n"
        "- casual conversation\n\n"
        "If useful information exists,\n"
        "return ONLY the fact that should be remembered.\n\n"
        "If there is nothing useful to remember,\n"
        "return:\n\n"
        "NONE\n"
    )

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract useful long-term memories."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    fact = response.choices[0].message.content

    # FIX: remove thinking text from models like qwen3
    if "</think>" in fact:
        fact = fact.split("</think>")[-1]

    fact = fact.strip().strip('"').strip()

    # FIX: "None", "NONE." and empty all mean "nothing to remember"
    # Also handle verbose models that add explanation before/after NONE
    if not fact or fact.upper().strip(" .") == "NONE":
        return "NONE"

    lines = [l.strip() for l in fact.splitlines() if l.strip()]
    if lines and lines[-1].upper().strip(" .") == "NONE":
        return "NONE"

    return fact
