# Day 03 — Prompt Engineering (System Prompts & Roles)

Part of the **AI_Agent_Journy** day-by-day learning series.

| Day | Topic |
|-----|-------|
| Day 01 | Ollama chatbot |
| Day 02 | AI assistant with memory |
| **Day 03** | **Prompt engineering — system prompts & role-based assistants** |

---

## 🎯 Goal of Day 3

Learn how a **system prompt** controls the AI's personality, tone and behaviour without changing the model.

- **Part 1 (P1):** one  system prompt, so the AI always acts as a *friendly teacher*.
- **Part 2 (P2):** the user picks a role from a menu, so the same model can become a teacher, Python expert, travel guide, coach or interviewer.

**Key idea:** Same model + different system prompt = different assistant.

---

## 📁 Folder Structure

```
Day_03_Prompt-Engineering/
├── Day03_P1/
│   └── assistant.py    # fixed-role assistant
└── Day03_P2/
    └── assistant.py    # role-selection assistant
```

---

## 🧠 Concept: What Is Prompt Engineering?

Prompt engineering means writing instructions so the model gives you the output you want.

Every chat request is a list of messages, and each message has a **role**:

| Role | Who writes it | Purpose |
|------|---------------|---------|
| `system` | Developer | Sets the AI's behaviour, personality and rules. Sent first. |
| `user` | Human | The question or input |
| `assistant` | Model | The model's previous replies (memory) |

The model reads the **system** message before everything else, so it shapes every answer in the conversation.

### What makes a good system prompt
1. **Role:** who the AI is (`You are a senior Python developer`)
2. **Task:** what it should do (`Explain programming concepts clearly`)
3. **Style / format:** how it should answer (`simple language`, `always include Python examples`)
4. **Rules:** constraints it must follow (`Ask one question at a time`)

---

## 🧩 Part 1 — One System Prompt

📁 `Day03_P1/assistant.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
messages = [
    {
        "role": "system",
        "content": "You are a friendly AI teacher. Explain every concept in simple language with real-life examples."
    }
]

while True:

    user_input = input("\nYou : ")
    # Save the user's message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )

    ai_reply = response.choices[0].message.content

    print("\nAI :", ai_reply)

    # Save the AI's reply
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )
```

### Code Explanation (Step by Step)

#### Step 1 — Imports
```python
from openai import OpenAI
from dotenv import load_dotenv
import os
```
- `OpenAI` is the client that talks to any OpenAI-compatible API (Ollama provides one).
- `load_dotenv` reads the config values into environment variables.
- `os` reads those values with `os.getenv()`.

#### Step 2 — Load configuration
```python
load_dotenv()
```
Loads `BASE_URL`, `API_KEY` and `MODEL`, which keeps settings out of the code.

#### Step 3 — Create the AI client
```python
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
```
Points the OpenAI client at the local Ollama server instead of OpenAI's cloud.

#### Step 4 — Print the banner
```python
print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
```
`"=" * 40` repeats the character 40 times to make a divider line.

#### Step 5 — Define the system prompt ⭐ (Day 3 focus)
```python
messages = [
    {
        "role": "system",
        "content": "You are a friendly AI teacher. Explain every concept in simple language with real-life examples."
    }
]
```
- The conversation list **starts** with a system message.
- The prompt breaks down into three parts:
  - **Role:** `friendly AI teacher`
  - **Style:** `simple language`
  - **Format rule:** `with real-life examples`
- Every answer in the session follows these instructions.

#### Step 6 — Chat loop
```python
while True:
    user_input = input("\nYou : ")
```
The loop runs until the user types `quit`.

#### Step 7 — Save the user's message (memory from Day 2)
```python
messages.append({"role": "user", "content": user_input})
```
Adds the question to the history so the model sees the full conversation.

#### Step 8 — Exit condition
```python
if user_input.lower() == "quit":
    print("\nAI  : Goodbye! Have a great day.")
    break
```
`.lower()` makes `QUIT`, `Quit` and `quit` all work.

#### Step 9 — Send the messages to the model
```python
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=messages
)
```
Sends **the system message, all user messages and all assistant messages** every time.

#### Step 10 — Read and print the reply
```python
ai_reply = response.choices[0].message.content
print("\nAI :", ai_reply)
```
`choices[0]` is the first (and only) answer the model generated.

#### Step 11 — Save the AI's reply
```python
messages.append({"role": "assistant", "content": ai_reply})
```
Stores the answer so follow-up questions have context.

### Flow
```
config → client → [system prompt] → loop:
   user input → append → quit? → send all messages → print reply → append reply
```

### 📤 Output — Part 1
$ python assistant.py 
========================================
      My AI Assistant
========================================

You : heloo

AI : Hello!

Welcome to our learning adventure together! I'm your friendly AI teacher, here to help you learn and understandnew concepts in simple and easy-to-understand language.

How's your day going so far? Ready to learn something new? Please tell me what you'd like to learn about, and I'll do my best to explain it in a way that's fun and easy to grasp!

(By the way, I noticed you started with a simple "hello" - great job starting with a positive note!)

You : quit

AI  : Goodbye! Have a great day.


**Observation:**
<!-- e.g. Did the AI explain simply with real-life examples? -->

---

## 🧩 Part 2 — Choose Your Assistant (Role Selection)

📁 `Day03_P2/assistant.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

roles = {
    "1": "You are a friendly school teacher. Explain every concept using simple language and real-life examples.",

    "2": "You are a senior Python developer. Explain programming concepts clearly and always include Python examples.",

    "3": "You are an experienced travel guide. Recommend places, food, transportation and travel tips.",

    "4": "You are a motivational coach. Encourage the user and give practical advice with a positive attitude.",

    "5": "You are a professional interviewer. Ask one interview question at a time and provide feedback after each answer."
}


print("\nChoose Your Assistant\n")

print("1. Teacher")
print("2. Python Expert")
print("3. Travel Guide")
print("4. Motivational Coach")
print("5. Interviewer")

choice = input("\nEnter your choice : ")

messages = [
    {
        "role": "system",
        "content": roles.get(
            choice,
            "You are a helpful AI assistant."
        )
    }
]


while True:

    user_input = input("\nYou : ")
    # Save the user's message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )

    ai_reply = response.choices[0].message.content

    print("\nAI :", ai_reply)

    # Save the AI's reply
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )
```

### Code Explanation (Step by Step)

Steps 1–4 (imports, config, client, banner) are the same as in Part 1.

#### Step 5 — Dictionary of roles ⭐
```python
roles = {
    "1": "You are a friendly school teacher. ...",
    "2": "You are a senior Python developer. ...",
    "3": "You are an experienced travel guide. ...",
    "4": "You are a motivational coach. ...",
    "5": "You are a professional interviewer. ..."
}
```
- Each **key** is a menu number, stored as a string because `input()` returns a string.
- Each **value** is the system prompt for that role.

| # | Role | What the prompt controls |
|---|------|--------------------------|
| 1 | Teacher | Simple language + real-life examples |
| 2 | Python Expert | Clear explanations + mandatory code examples |
| 3 | Travel Guide | Places, food, transport, tips |
| 4 | Motivational Coach | Positive tone + practical advice |
| 5 | Interviewer | One question at a time + feedback (controls the conversation flow) |

#### Step 6 — Show the menu
```python
print("1. Teacher")
...
print("5. Interviewer")
```

#### Step 7 — Get the user's choice
```python
choice = input("\nEnter your choice : ")
```

#### Step 8 — Build the system message from the choice
```python
messages = [
    {
        "role": "system",
        "content": roles.get(choice, "You are a helpful AI assistant.")
    }
]
```
- `roles.get(choice, default)` returns the matching prompt.
- Invalid input (e.g. `9` or `abc`) falls back to `"You are a helpful AI assistant."` instead of crashing.

#### Steps 9–14 — Chat loop
The loop is the same as Part 1 Steps 6–11: input → save → quit check → send → print → save reply.

### Flow
```
config → client → show menu → choice → roles.get() → [system prompt] → chat loop
```

### 📤 Output — Part 2

#### Role 1 — Teacher
```
$ python assistant.py 
========================================
      My AI Assistant
========================================

Choose Your Assistant

1. Teacher
2. Python Expert
3. Travel Guide
4. Motivational Coach
5. Interviewer

Enter your choice : 1

You : hello

AI : Hello! *big smile* Welcome to our learning community! I'm so excited to meet you and help you learn new things. Don't worry, I'll explain everything in a way that's easy to understand and fun.

What subject or topic would you like to learn about today? Do you have a specific question or subject in mind, or would you like to explore a new one?

You : quit

AI  : Goodbye! Have a great day.
```



#### Role 5 — Interviewer
```
$ python assistant.py 
========================================
      My AI Assistant
========================================

Choose Your Assistant

1. Teacher
2. Python Expert
3. Travel Guide
4. Motivational Coach
5. Interviewer

Enter your choice : 5

You : hello

AI : Hello! Welcome to our mock interview. I'd like to start by asking a question to get us started. Here it is:
Can you tell me a little bit about yourself and why you're interested in this role?

Please respond as if you were in a real interview. I'll give you feedback on your answer afterwards!

You : quit

AI  : Goodbye! Have a great day.
```



**Observation:**
<!-- e.g. Same question, different roles: how did the answers differ? -->

---

## 🔍 P1 vs P2

| | Part 1 | Part 2 |
|---|--------|--------|
| System prompt | Hard-coded | Chosen at runtime |
| Roles | 1 | 5 + default |
| New concept | System role | Dictionary of prompts + `.get()` fallback |

---

## ⚠️ Known Limitations / Improvements

1. `quit` is appended to `messages` before the exit check. This is harmless but unnecessary; move the quit check above the `append`.
2. There is no `try/except` around the API call, so the script crashes if Ollama is not running.
3. The history grows without limit, so long chats can exceed the model's context window.
4. The role can't be changed mid-chat; you have to restart the script.
5. `qwen3` may print `<think>...</think>` reasoning blocks. These can be stripped before printing.

---

## ✅ Key Takeaways

- The **system prompt** is the main tool for controlling an AI's behaviour.
- A good prompt states the **role, task, style and rules**.
- One model can power many assistants just by swapping the system prompt.
- `dict.get(key, default)` gives a safe fallback for user input.

---

