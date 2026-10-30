# Day 2 — AI Assistant with Memory

On Day 1 the assistant answered each question in isolation: it forgot everything after every reply. Day 2 fixes that. The assistant now keeps a **conversation history** (its "memory") and sends the full history to the model on every turn, so it can answer follow-up questions like *"What did I just ask you?"*.

The model runs **locally with Ollama** and is called through the **OpenAI Python SDK**, using Ollama's OpenAI-compatible API.

---

## Project Structure

Day 2 lives inside the shared `AI_Agent_Journy` repo. The virtual environment, `requirements.txt` and `.env` are all at the **project root** and shared by every day — Day 2 has no setup files of its own.

```
AI_Agent_Journy/
├── venv/                              # Shared virtual environment (not committed)
├── .env                               # Shared config (not committed)
├── .env.example                       # Template for .env (committed)
├── .gitignore
├── requirements.txt                   # Shared dependencies
├── Day_01_ollama-chatbot/
└── Day_02_AI-Assistant-with-memory/
    ├── README.md                      # This file
    ├── Day02_P2/
    │   └── assistant.py               # Chat with memory + raw history dump
    └── Day02_P3/
        └── assistant.py               # Chat with memory + clean, formatted history
```

| Part | What it adds |
|------|--------------|
| **P2** | Stores every user and AI message in a `messages` list and sends the whole list to the model. Prints the history as raw Python dictionaries. |
| **P3** | Same logic as P2, but prints the history in a readable `Role : content` format. |

> **Why no `.env` inside the Day folders?** `load_dotenv()` searches upward from the script's folder and uses the **first** `.env` it finds. One root `.env` serves every day. A leftover `.env` inside a Day folder would override the root one, so don't create one there.

---

## How the Memory Works

Language models are **stateless**: they remember nothing between API calls. "Memory" is created by the program, not the model:

1. Keep a Python list called `messages`.
2. Every time the user types something, append `{"role": "user", "content": ...}`.
3. Send the **entire list** to the model.
4. Append the model's answer as `{"role": "assistant", "content": ...}`.
5. Repeat. Each new request now contains the full conversation, so the model has context.

```
Turn 1 sends:  [user1]
Turn 2 sends:  [user1, assistant1, user2]
Turn 3 sends:  [user1, assistant1, user2, assistant2, user3]
```

The list grows every turn — that growing list *is* the memory.

---

## Step-by-Step Setup

Commands below are for **Git Bash** on Windows. If you already set up the project on Day 1, Steps 1–3 are done — skip to Step 4.

### Step 1 — Go to the project root

```bash
cd "/d/AI Agents/AI_Agent_Journy"
```

### Step 2 — Activate the shared virtual environment

```bash
source venv/Scripts/activate
```

You should see `(venv)` in the terminal. (CMD/PowerShell: `venv\Scripts\activate`.)

If `venv` doesn't exist yet, create it first:

```bash
python -m venv venv
```

### Step 3 — Install the packages

`requirements.txt` at the root contains:

```
openai
python-dotenv
```

Install with the venv's own Python so packages land inside the venv:

```bash
python -m pip install -r requirements.txt
```

| Package | Purpose |
|---------|---------|
| `openai` | Client library used to send chat requests (works with Ollama's OpenAI-compatible endpoint) |
| `python-dotenv` | Loads settings from the `.env` file into environment variables |

### Step 4 — Create the `.env` file

```bash
cp .env.example .env
```

Edit `.env` so it contains:

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama

MODEL=llama3.2
# MODEL=qwen3:4b
```

| Variable | Meaning |
|----------|---------|
| `BASE_URL` | Address of the API. `/v1` is Ollama's OpenAI-compatible endpoint. |
| `API_KEY` | Ollama does not check the key, but the OpenAI client requires one, so any text works. For a cloud provider, put your real key here. |
| `MODEL` | Which model to use. Must match a name shown by `ollama list`. Only the uncommented `MODEL` line is used — move the `#` to switch. |

### Step 5 — Check the model is downloaded

```bash
ollama list
```

If your chosen model isn't listed, download it once (it stays on disk afterwards):

```bash
ollama pull llama3.2
```

Make sure Ollama is running (the desktop app starts it automatically; otherwise run `ollama serve`).

**Which model?**

| Model | Size | Notes |
|-------|------|-------|
| `llama3.2` (Meta, 3B) | 2.0 GB | Faster, answers directly. Recommended for this project. |
| `qwen3:4b` (Alibaba, 4B) | 2.5 GB | Reasoning model — better at maths/logic/code, but slower and may print `<think>...</think>` before answering. |

### Step 6 — Run the assistant

```bash
cd Day_02_AI-Assistant-with-memory/Day02_P3
python assistant.py
```

Type messages and press Enter. Type `quit` to exit.

To run Part 2 instead:

```bash
cd ../Day02_P2
python assistant.py
```

### Step 7 — Commit to GitHub

Make sure `.gitignore` at the root contains:

```
venv/
.env
```

Then:

```bash
cd "/d/AI Agents/AI_Agent_Journy"
git status          # venv/ and .env must NOT appear
git add .
git commit -m "Day 2: AI assistant with memory"
git push
```

---

## Code — Part 2 (`Day02_P2/assistant.py`)

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
messages = []
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

    print("\n---------- Conversation History ----------")

    for message in messages:
        print(message)

    print("------------------------------------------")
```

### Explanation (block by block)

| Code | What it does |
|------|--------------|
| `from openai import OpenAI` | Imports the client class used to talk to the model. |
| `from dotenv import load_dotenv` / `import os` | Tools to read the `.env` file and environment variables. |
| `load_dotenv()` | Reads `.env` and loads `BASE_URL`, `API_KEY`, `MODEL` into the environment. |
| `client = OpenAI(base_url=..., api_key=...)` | Creates the client. Pointing `base_url` at Ollama makes the OpenAI SDK talk to your local model. |
| `print("=" * 40)` | Prints a banner line of 40 `=` characters. |
| `messages = []` | **The memory.** An empty list, created once *before* the loop so it survives every turn. |
| `while True:` | Keeps the chat running until `break`. |
| `user_input = input("\nYou : ")` | Waits for the user to type a message. |
| `messages.append({"role": "user", ...})` | Saves the user's message into memory. |
| `if user_input.lower() == "quit": ... break` | Exits when the user types `quit` (any capitalisation). |
| `client.chat.completions.create(model=..., messages=messages)` | Sends the **whole history** to the model — this is why it remembers. |
| `response.choices[0].message.content` | Extracts the text of the model's reply. |
| `messages.append({"role": "assistant", ...})` | Saves the AI's reply into memory so the next turn includes it. |
| `for message in messages: print(message)` | Prints the full history as raw dictionaries, so you can *see* the memory growing. |

### Sample output (P2)

Run with `MODEL=llama3.2`:

```
$ python assistant.py
========================================
      My AI Assistant
========================================

You : hello

AI : Hello! How can I assist you today?

---------- Conversation History ----------
{'role': 'user', 'content': 'hello'}
{'role': 'assistant', 'content': 'Hello! How can I assist you today?'}
------------------------------------------

You : my name is chandan , can you gase my age ?

AI : Hello Chandan, I don't know your age, as I'm a conversational AI and don't have any prior information about you. I was just pretending to know. Would you like to share your age with me?

---------- Conversation History ----------
{'role': 'user', 'content': 'hello'}
{'role': 'assistant', 'content': 'Hello! How can I assist you today?'}
{'role': 'user', 'content': 'my name is chandan , can you gase my age ?'}
{'role': 'assistant', 'content': "Hello Chandan, I don't know your age, as I'm a conversational AI and don't have any prior information about you. I was just pretending to know. Would you like to share your age with me?"}
------------------------------------------

You : 25

AI : Happy 25th birthday, Chandan! May this year bring you happiness, success, and all the things you desire! What have been your favorite experiences or moments from your 25th year so far?

---------- Conversation History ----------
{'role': 'user', 'content': 'hello'}
{'role': 'assistant', 'content': 'Hello! How can I assist you today?'}
{'role': 'user', 'content': 'my name is chandan , can you gase my age ?'}
{'role': 'assistant', 'content': "Hello Chandan, I don't know your age, as I'm a conversational AI and don't have any prior information about you. I was just pretending to know. Would you like to share your age with me?"}
{'role': 'user', 'content': '25'}
{'role': 'assistant', 'content': 'Happy 25th birthday, Chandan! May this year bring you happiness, success, and all the things you desire! What have been your favorite experiences or moments from your 25th year so far?'}
------------------------------------------

You : bye

AI : Bye Chandan! Take care and have a great day!

---------- Conversation History ----------
{'role': 'user', 'content': 'hello'}
{'role': 'assistant', 'content': 'Hello! How can I assist you today?'}
{'role': 'user', 'content': 'my name is chandan , can you gase my age ?'}
{'role': 'assistant', 'content': "Hello Chandan, I don't know your age, as I'm a conversational AI and don't have any prior information about you. I was just pretending to know. Would you like to share your age with me?"}
{'role': 'user', 'content': '25'}
{'role': 'assistant', 'content': 'Happy 25th birthday, Chandan! May this year bring you happiness, success, and all the things you desire! What have been your favorite experiences or moments from your 25th year so far?'}
{'role': 'user', 'content': 'bye'}
{'role': 'assistant', 'content': 'Bye Chandan! Take care and have a great day!'}
------------------------------------------

You :
```

**What this shows:**

- **Memory works.** The name "Chandan" was given in turn 2, and the AI still uses it in turns 3 and 4 because the full history is sent each time.
- **Context works.** The reply `25` alone makes sense to the model only because it can see the earlier question about age.
- **The history grows** by 2 entries (user + assistant) every turn.
- **`bye` does not exit.** The loop only stops on `quit`, so `bye` is sent to the model as a normal message.

---

## Code — Part 3 (`Day02_P3/assistant.py`)

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
messages = []
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

    print("\n========== Conversation History ==========")

    for message in messages:
        print(f"{message['role'].title()} : {message['content']}")

    print("==========================================")
```

### What changed from P2

Only the history printout is different:

```python
# P2 — raw dictionary
print(message)

# P3 — formatted line
print(f"{message['role'].title()} : {message['content']}")
```

| Piece | Meaning |
|-------|---------|
| `f"..."` | f-string: lets you put variables inside `{}` in a string. |
| `message['role']` | `"user"` or `"assistant"`. |
| `.title()` | Capitalises the first letter → `"User"`, `"Assistant"`. |
| `message['content']` | The actual text of the message. |

### Sample output (P3)

```
$ python assistant.py
========================================
      My AI Assistant
========================================

You : hi

AI : Hello! How can I assist you today?

========== Conversation History ==========
User : hi
Assistant : Hello! How can I assist you today?
==========================================

You : my name is ckm

AI : Hello Ckm! It's nice to meet you. Is there something I can help you with, or would you like to chat?

========== Conversation History ==========
User : hi
Assistant : Hello! How can I assist you today?
User : my name is ckm
Assistant : Hello Ckm! It's nice to meet you. Is there something I can help you with, or would you like to chat?
==========================================

You :
```

Same memory behaviour as P2. The history is just much easier to read: `User :` / `Assistant :` instead of raw `{'role': ..., 'content': ...}` dictionaries.

---

## Quick Command Summary

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
python -m pip install -r requirements.txt
cp .env.example .env              # first time only, then set MODEL
ollama list                       # check model exists
cd Day_02_AI-Assistant-with-memory/Day02_P3
python assistant.py
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'openai'` | Venv active but package not installed in it. Run `python -m pip install -r requirements.txt`. Check `which python` points to `.../AI_Agent_Journy/venv/Scripts/python`. |
| `Connection refused` / `APIConnectionError` | Ollama isn't running. Start it with `ollama serve` or open the Ollama app. |
| `model '...' not found` | `MODEL` in `.env` doesn't match `ollama list`. Fix the name or `ollama pull` it. |
| `api_key must be set` | No `.env` at the project root. Run `cp .env.example .env`. |
| Changing `.env` has no effect | An old `.env` inside a Day folder is overriding the root one. Find and delete it: `find . -name ".env" -not -path "./venv/*"` — only `./.env` should remain. |
| `ollama pull` downloading again | It only downloads models not in `ollama list`. Once finished, a model is never re-downloaded. |
| Reply contains `<think>...</think>` | You're using `qwen3:4b` (a reasoning model). Switch to `llama3.2` to avoid it. |
| Responses get slower over time | History grows every turn, so each request is larger. Restart the script to clear memory. |

---

## Notes & Possible Improvements

- **`quit` is saved before exiting.** The user message is appended *before* the quit check. It's harmless here because the loop ends immediately, but moving the `if user_input.lower() == "quit"` check above the `append` is cleaner.
- **Memory is temporary.** It lives in RAM and is lost when the program closes. Saving `messages` to a JSON file would make it persistent.
- **Unlimited growth.** Long chats can exceed the model's context window. A common fix is to keep only the last N messages, e.g. `messages[-20:]`.
- **System prompt.** Adding `{"role": "system", "content": "You are a helpful assistant."}` as the first item in `messages` lets you control the assistant's personality.
- **Error handling.** Wrapping the API call in `try/except` stops the program from crashing if Ollama is offline.

---

## Key Takeaways

1. LLMs don't remember anything on their own — every API call is independent.
2. Memory = storing the conversation in a list and sending it all on every request.
3. Each message has a `role` (`user` / `assistant` / `system`) and `content`.
4. Using `base_url`, the same OpenAI code works with local models (Ollama) or cloud providers just by changing `.env`.