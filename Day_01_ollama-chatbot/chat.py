import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load values from the .env file
load_dotenv()

# 2. Create the client (points to Ollama instead of OpenAI)
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

# 3. Create the response with arguments
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is Docker in 2 lines?"},
    ],
    temperature=0.7,
    max_tokens=300,
)

# 4. Print the answer
print(response.choices[0].message.content)
