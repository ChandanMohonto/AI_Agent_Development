# Day 04 — AI Tools: Teach Your AI Assistant to Use Tools 🛠️

Part of the **AI_Agent_Journy** day-by-day learning series.

| Day | Topic |
|-----|-------|
| Day 01 | Ollama chatbot |
| Day 02 | AI assistant with memory |
| Day 03 | Prompt engineering — system prompts & roles |
| **Day 04** | **AI tools — teach the assistant to use Python functions** |

---

## 🎯 Goal of Day 4

Give the AI assistant **tools**: small Python functions it can use to do things a language model can't do reliably on its own.

By the end of the day, the assistant can:

- ⏰ tell the **real** current date and time
- 🎲 roll a dice
- 🔐 generate a secure password

…and still chat normally with the AI for everything else.

---

## 🤔 What Is an AI Tool?

An **AI tool** is a normal function (here, a Python function) that the assistant can **call** to get a real result, instead of guessing.

> **Model = the brain.** It understands language and writes answers.
> **Tool = the hands.** It *does* something: reads the clock, does maths, calls an API, searches files.

### Why do we need tools?

A language model only predicts text based on what it learned during training. That means:

| Question | Model alone | With a tool |
|----------|-------------|-------------|
| "What time is it?" | ❌ Has no clock; it will guess or say it doesn't know | ✅ `get_current_time()` reads the system clock |
| "Roll a dice" | ⚠️ Not truly random; LLMs repeat favourite numbers | ✅ `random.randint(1, 6)` |
| "Give me a password" | ⚠️ Not secure; the text could be predictable | ✅ `secrets.choice()` uses a cryptographically secure generator |

**Rule of thumb:** if the answer must be **real, current, exact or random**, use a tool. If the answer is **explanation, writing or conversation**, use the model.

### How does the assistant use a tool?

Every message goes through a **decision step**:

```
User message
     │
     ▼
Does this message need a tool?
     │
 ┌───┴────┐
YES       NO
 │         │
 ▼         ▼
Run the    Send the message
Python     to the AI model
function   (normal chat)
 │         │
 └───┬─────┘
     ▼
 Show answer
```

In Day 4 the decision is made with **simple keyword rules** in Python (e.g., "if the message contains *time* → use the time tool"). Real AI agents let the **model itself** pick the tool (called *function calling*). That's the natural next step, but keyword rules make the idea easy to see first.

---

## 🧩 The 4 Parts at a Glance

| Part | What we build | New files |
|------|---------------|-----------|
| **P1** | Write 3 tools as plain Python functions and test them alone, with no AI involved | `tools.py`, `test_tools.py` |
| **P2** | Connect the tools to the AI assistant using `if` keyword checks inside the chat loop | `assistant.py` |
| **P3** | Refactor: move all tool decisions into one **Tool Manager** and test it alone | `tool_manager.py`, `test_tool_manager.py` |
| **P4** | Plug the Tool Manager into the assistant, so the chat loop becomes short and clean | `assistant.py` (updated) |

Each part **builds on the previous one**: P2 reuses P1's `tools.py`, P3 reuses P2's `assistant.py` unchanged, and so on.

---

## 📁 Folder Structure

```
Day_04_AI-Tools/
├── README.md
├── Day04_P1/
│   ├── tools.py              # the 3 tools
│   └── test_tools.py         # test the tools alone
├── Day04_P2/
│   ├── tools.py
│   ├── test_tools.py
│   └── assistant.py          # tools connected with if-checks
├── Day04_P3/
│   ├── tools.py
│   ├── test_tools.py
│   ├── tool_manager.py       # all tool decisions in one place
│   ├── test_tool_manager.py  # test the manager alone
│   └── assistant.py          # same as P2
└── Day04_P4/
    ├── tools.py
    ├── test_tools.py
    ├── tool_manager.py
    ├── test_tool_manager.py
    └── assistant.py          # uses the Tool Manager
```

> Setup (venv, `requirements.txt`, `.env`) is shared at the **project root**, the same as in previous days. Day 4 needs **no new packages**: `datetime`, `random`, `secrets` and `string` are all built into Python.

---

## ▶️ How to Run

From the project root, with the venv active:

```bash
cd Day_04_AI-Tools/Day04_P1
python test_tools.py

cd ../Day04_P2
python assistant.py

cd ../Day04_P3
python test_tool_manager.py
python assistant.py

cd ../Day04_P4
python test_tool_manager.py
python assistant.py
```

Type `quit` to exit the assistant.

---

# Part 1 — Building the Tools 🔧

**Goal:** write three tools as normal Python functions and prove they work **before** connecting any AI.

> 💡 **Why test tools alone first?** If something breaks later, you'll know whether the bug is in the tool or in the AI connection. Test small pieces first, then join them.

### `tools.py`

```python
from datetime import datetime

def get_current_time():
    """Return the current date and time."""

    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

import random

def roll_dice():
    """Return a random number between 1 and 6."""

    return random.randint(1, 6)

import secrets
import string

def generate_password(length=12):
    """Generate a secure random password."""

    characters = (
        string.ascii_letters +
        string.digits +
        string.punctuation
    )

    password = ""

    for _ in range(length):
        password += secrets.choice(characters)

    return password
```

### Step-by-step explanation

**Tool 1 — Current date and time**

```python
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
```

| Code | Meaning |
|------|---------|
| `datetime.now()` | Reads the computer's clock right now. |
| `.strftime(...)` | Formats the date/time as text. |
| `%d-%m-%Y` | Day-Month-Year → `01-11-2026` |
| `%I:%M:%S %p` | 12-hour time with AM/PM → `04:35:12 PM` |

**Tool 2 — Dice roller**

```python
import random

def roll_dice():
    return random.randint(1, 6)
```

`random.randint(1, 6)` returns a whole number from 1 to 6, **including** both 1 and 6.

**Tool 3 — Secure password generator**

```python
import secrets
import string

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ""
    for _ in range(length):
        password += secrets.choice(characters)
    return password
```

| Code | Meaning |
|------|---------|
| `length=12` | Default parameter: 12 characters unless you pass another number, e.g. `generate_password(20)`. |
| `string.ascii_letters` | `a–z` and `A–Z` |
| `string.digits` | `0–9` |
| `string.punctuation` | Symbols like `!@#$%&*` |
| `secrets.choice(characters)` | Picks one random character **securely**. |
| `for _ in range(length)` | Repeat `length` times. `_` means "I don't need the loop counter". |

> 🔐 **`secrets` vs `random`:** `random` is fine for games (dice). For passwords, always use `secrets`, because its output can't be predicted.

**Docstrings:** each function starts with `"""..."""`. This describes what the tool does. Later, when the **AI** chooses tools by itself, these descriptions are what it reads to decide.

### `test_tools.py`

```python
from tools import get_current_time,roll_dice,generate_password

print(get_current_time())
print(roll_dice())
print(generate_password())
```

Imports the three tools and calls each one once. There's no AI, Ollama or `.env` here, so it runs instantly.

### 📤 Output — Part 1

#### `python test_tools.py`
```
$ python test_tools.py
01-11-2026 11:32:23 AM
3
C{QnB%:<tnVb
```

**Observation:**
<!-- e.g. Run it twice — time changes, dice and password are different each time. -->

---

# Part 2 — Connecting Tools to the AI Assistant 🔌

**Goal:** inside the chat loop, check each message. If it asks for a tool, run the tool. Otherwise, send the message to the AI.

This is the Day 3 role-based assistant plus a **decision step** at the top of the loop.

### `assistant.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

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

    if "time" in user_input.lower():

        print("\nAI :", get_current_time())

        continue

    if "dice" in user_input.lower():

        print("\nAI : You rolled", roll_dice())

        continue

    if "password" in user_input.lower():

        print("\nAI :", generate_password())

        continue


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

### Step-by-step explanation

**1. Import the tools**

```python
from tools import (
    get_current_time,
    roll_dice,
    generate_password
)
```

Brings in the three functions from `tools.py` (same folder). The brackets let the import span several lines.

**2. Config, client, roles, menu: same as Day 3**

`load_dotenv()` → `OpenAI(...)` client → `roles` dictionary → menu → `choice` → first message is the **system prompt** chosen with `roles.get(choice, default)`.

**3. The decision step (new)**

```python
if "time" in user_input.lower():
    print("\nAI :", get_current_time())
    continue
```

| Code | Meaning |
|------|---------|
| `user_input.lower()` | Lower-case the message so `Time`, `TIME`, `time` all match. |
| `"time" in ...` | `True` if the word appears **anywhere** in the message. |
| `get_current_time()` | Run the tool. |
| `continue` | **Skip the rest of the loop** (no AI call) and wait for the next message. |

The same pattern is repeated for `"dice"` → `roll_dice()` and `"password"` → `generate_password()`.

**4. No tool matched → normal AI chat**

```python
messages.append({"role": "user", "content": user_input})
...
response = client.chat.completions.create(model=os.getenv("MODEL"), messages=messages)
```

This is the same memory-based chat as Day 2/3: save the message, send the full history, print and save the reply.

> ⚡ **Notice:** tool answers are **instant**, because they never reach the model. Only normal questions wait for the AI.

### Flow

```
input → contains "time"?     → get_current_time()  → print → next message
      → contains "dice"?     → roll_dice()         → print → next message
      → contains "password"? → generate_password() → print → next message
      → otherwise            → AI model (with memory) → print → next message
```

### 📤 Output — Part 2

#### Time tool
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

Enter your choice : 4

You : hi, 

AI : Hello! It's so great to connect with you! How's your day going so far? Is there something on your mind that you'd like to talk about or work on? I'm all ears, and I'm here to listen, offer advice, and help you shine your light! What's new and exciting in your world?

You : how i remove negitivity?

AI : Removing negativity is a great goal to have! It's not always easy, but it's definitely possible with the right mindset and strategies. Here are some practical tips to help you remove negativity from your life:

1. **Recognize and acknowledge**: The first step to removing negativity is to acknowledge it. Be aware of the thoughts, feelings, and emotions that are holding you back. Try to identify the sources of negativity in your life, such as relationships, thoughts, or circumstances.
2. **Practice self-care**: Take care of yourself physically, emotionally, and mentally. Engage in activities that bring you joy, relaxation, and fulfillment. This will help you build a positive foundation for dealing with negativity.
3. **Challenge negative thoughts**: When negative thoughts arise, challenge them with positive affirmations. Replace self-critical thoughts with encouraging, realistic ones. For example, "I'm not good enough" becomes "I'm capable and deserving of success."
4. **Surround yourself with positivity**: Spend time with people who uplift and support you. Consume media, books, or podcasts that inspire and motivate you. Limit your exposure to negative news or social media that can drain your energy.
5. **Take a break**: Sometimes, taking a break from a situation or person that's causing negativity can be incredibly helpful. Give yourself permission to step back and recharge before returning to the challenging environment.
6. **Practice gratitude**: Focus on the good things in your life. Make a gratitude journal, write down three things you're thankful for each day, or share your gratitude with a friend or family member.
7. **Take care of your relationships**: Nurture your relationships with people who positively impact your life.Set boundaries with those who drain your energy or bring you down. Invest in relationships that uplift and support you.
8. **Focus on the present**: Rather than dwelling on the past or worrying about the future, bring your attention to the present moment. Practice mindfulness techniques, such as meditation or deep breathing, to stay groundedand centered.
9. **Reframe challenges as opportunities**: View challenges as opportunities for growth and learning. Ask yourself, "What can I learn from this experience?" or "How can I grow as a person by facing this challenge?"
10. **Celebrate your successes**: Acknowledge and celebrate your achievements, no matter how small they may seem. This will help boost your confidence and reinforce a positive mindset.

Remember, removing negativity is a process that takes time, effort, and patience. Be gentle with yourself, and don't be too hard on yourself when you slip up. You got this!

You : quit

AI  : Goodbye! Have a great day.
(venv) 
```

#### Dice tool
```
hoose Your Assistant

1. Teacher
2. Python Expert
3. Travel Guide
4. Motivational Coach
5. Interviewer

Enter your choice : 2

You : roll a dice

AI : You rolled 3
```







---

# Part 3 — Building a Tool Manager 🧰

**Problem with P2:** every new tool means adding another `if` block **inside the chat loop**. With 10 tools, `assistant.py` becomes long and messy, and the tool logic can't be tested without starting the whole AI.

**Solution:** move all tool decisions into **one function in its own file**, the **Tool Manager**.

```
Before (P2):  assistant.py = chat + menu + tool decisions
After  (P3):  assistant.py = chat + menu
              tool_manager.py = tool decisions   ← one job, one file
```

This is called **refactoring**: changing the structure of code without changing what it does.

> In P3, `assistant.py` is **unchanged** from P2. We build and test the Tool Manager first, and connect it in P4.

### `tool_manager.py`

```python
from tools import (
    get_current_time,
    roll_dice,
    generate_password
)

def execute_tool(user_input):

    text = user_input.lower()

    if "time" in text or "clock" in text:
        return get_current_time()

    if "dice" in text or "die" in text:
        return f"You rolled {roll_dice()}"

    if "password" in text:
        return generate_password()

    return None
```

### Step-by-step explanation

| Code | Meaning |
|------|---------|
| `def execute_tool(user_input):` | One entry point: give it any message and it decides. |
| `text = user_input.lower()` | Lower-case once and reuse it. |
| `"time" in text or "clock" in text` | **More keywords per tool**, so it understands more ways of asking (*"What's the clock?"*). |
| `"dice" in text or "die" in text` | Handles singular "die" too. |
| `return f"You rolled {roll_dice()}"` | The manager returns a **ready-to-print sentence**. |
| `return None` | **No tool matched.** This is the signal for the assistant to ask the AI instead. |

**Key design:** the function **returns** a result instead of printing it. The caller decides what to do with it. That makes it reusable and easy to test.

### `test_tool_manager.py`

```python
from tool_manager import execute_tool

print(execute_tool("What time is it?"))

print(execute_tool("Roll a dice"))

print(execute_tool("Generate a password"))

print(execute_tool("Explain Python"))
```

Tests the decision-making alone. The 4th case, `"Explain Python"`, needs no tool, so it should print `None`.

### 📤 Output — Part 3

#### `python test_tool_manager.py`
```
$ python test_tool_manager.py 
01-11-2026 11:53:08 AM
You rolled 4
tn<D\2&$(!`P
None
```

**Observation:**
<!-- e.g. First three return tool results; "Explain Python" returns None. -->

---

# Part 4 — Integrating the Tool Manager with the Assistant ✅

**Goal:** replace all the `if` blocks in the chat loop with **one call** to the Tool Manager.

### `assistant.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

from tools import (
    get_current_time,
    roll_dice,
    generate_password
)

from tool_manager import execute_tool


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

    tool_result = execute_tool(user_input)

    if tool_result:

        print("\nAI :", tool_result)

        continue

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

### What changed from P2/P3

```python
# P2 / P3 — three separate if-blocks in the loop
if "time" in user_input.lower():
    print("\nAI :", get_current_time())
    continue
if "dice" in user_input.lower():
    ...
if "password" in user_input.lower():
    ...

# P4 — one call
tool_result = execute_tool(user_input)

if tool_result:
    print("\nAI :", tool_result)
    continue
```

| Code | Meaning |
|------|---------|
| `from tool_manager import execute_tool` | Import the manager. |
| `tool_result = execute_tool(user_input)` | Ask the manager: "Does this need a tool?" |
| `if tool_result:` | A string means a tool ran. `None` counts as **False**, which means no tool was used. |
| `print(...)` + `continue` | Show the tool result and skip the AI. |
| *(otherwise)* | Fall through to normal AI chat, unchanged. |

**Result:** adding a new tool now only touches `tools.py` (write the function) and `tool_manager.py` (add one `if`). **`assistant.py` never changes again.** 🎉

### Flow

```
config → client → role menu → system prompt
   │
   ▼
loop: input → execute_tool(input)
                 │
        result? ─┼─ yes → print result → next message
                 │
                 no (None) → AI model with memory → print → next message
```

### 📤 Output — Part 4

#### Choose role + time tool
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

You : why 2*2 =4

AI : Let's break it down in a way that's easy to understand.

You know how we can count things, like 1, 2, 3? And how we can add numbers together, like 1 + 1 = 2?

Well, when we multiply, we're basically adding a number a certain number of times. For example, if we have 3 groups of 3 pencils, we can count the total number of pencils by adding 3 + 3 + 3.

So, when we multiply 2 by 2, we're asking ourselves, "How many groups of 2 do we have?" And the answer is, 2 groups of 2 is like 1 + 1.

Think of it like having 2 toy boxes, and each toy box has 2 blocks in it. We can count the total number of blocks by adding 2 + 2, which gives us 4 blocks.

The math problem 2 * 2 says, "2 groups of 2 blocks," and the answer is indeed 4 blocks! That's why 2 * 2 = 4.

Does that make sense?

You : roll a dice

AI : You rolled 4

You : generate a password

AI : lD}X|v6s=3ly

You : time and date now

AI : 01-11-2026 11:57:38 AM

You : am i a good coder ?

AI : That's a great question, but the answer is not just a simple "yes" or "no". Being a good coder is like being a good listener or a good athlete - it takes practice, patience, and dedication.

Here's the thing: coding is like having a superpower that helps us solve problems and create really cool things! But just like how you need to practice riding a bike to get better at it, you need to keep learning and practicing coding to become better.

Think of it like this: every good programmer started somewhere. They wrote their first lines of code, made mistakes, learned from them, and kept going.

So, here are some tips to help you become a better coder:

1. **Practice, practice, practice**: Try new things, work on small projects, and participate in coding challenges.
2. **Learn from others**: Read books, watch tutorials, and join online communities to learn from other coders.
3. **Ask for help**: Don't be afraid to ask your teachers, parents, or online communities for help when you're stuck.
4. **Be patient**: Coding can be tricky, and it's okay to make mistakes. Keep trying, and you'll get better with time.
5. **Find a project you love**: Working on projects that excite you can help you stay motivated and improve your coding skills.

Remember, everyone learns at their own pace, and it's okay to start small. You just need to keep showing up, trying new things, and having fun!

So, am you a good coder yet? Well, maybe not yet, but you're on the right track! Keep learning, practicing, and having fun, and you'll get there!

You : 
```


<!-- e.g. Same behaviour as P2, but the code is much cleaner. -->

---

## 🔍 P1 → P4 Comparison

| | P1 | P2 | P3 | P4 |
|---|----|----|----|----|
| Tools exist | ✅ | ✅ | ✅ | ✅ |
| Connected to AI | ❌ | ✅ | ✅ | ✅ |
| Where tool decisions live | — | Inside chat loop | `tool_manager.py` (not connected yet) | `tool_manager.py` |
| Keywords per tool | — | 1 | 1–2 | 1–2 |
| Testable without AI | Tools | Tools | Tools + decisions | Tools + decisions |
| Adding a new tool touches `assistant.py`? | — | Yes | — | **No** |

---

## ⚠️ Known Limitations / Improvements

1. **Keyword matching is fragile.** The check is "word appears anywhere", so false matches happen:
   - "Some**time**s I feel tired" → time tool ❌
   - "My **die**t plan" / "I stu**die**d" → dice tool ❌
   - "How do I make a strong **password**?" → generates a password instead of explaining ❌

   Fix ideas: match whole words with `re.search(r"\btime\b", text)`, or let the AI choose the tool (function calling).
2. **Tool results aren't saved to memory.** Because of `continue`, the tool answer never goes into `messages`. If you ask *"What time is it?"* and then *"What did you just tell me?"*, the AI won't know.
3. **The password length can't be changed from chat.** `generate_password()` always uses 12. "Give me a 20-character password" still gives 12.
4. **Unused imports in P4.** `assistant.py` still imports `get_current_time`, `roll_dice` and `generate_password`, but only the Tool Manager uses them now. They can be removed.
5. **`quit` is appended to `messages` before the exit check.** This is harmless, but the check can be moved above the `append`.
6. **No error handling.** If Ollama isn't running, the AI call crashes the script. Wrap it in `try/except`.

---

## ✅ Key Takeaways

- **Model = brain, tools = hands.** Use tools for anything real, current, exact or random.
- Every message needs a **decision**: tool or AI?
- **Test tools alone first**, then connect them.
- A **Tool Manager** keeps decisions in one place, so the assistant stays clean and new tools are easy to add.
- Return values (not prints) make functions **reusable and testable**.
- Use `secrets` for anything security-related, and `random` for games.

---

## ➡️ Next: Day 05
<!-- add next topic -->