# Day 05 — Document AI: Teach Your AI Assistant to Read Files 📄

Part of the **AI_Agent_Journy** day-by-day learning series.

| Day | Topic |
|-----|-------|
| Day 01 | Ollama chatbot |
| Day 02 | AI assistant with memory |
| Day 03 | Prompt engineering — system prompts & roles |
| Day 04 | AI tools — teach the assistant to use Python functions |
| **Day 05** | **Document AI — read, summarize, explain and question files** |

---

## 🎯 Goal of Day 5

Teach the assistant to work with **your own documents**.

By the end of the day, the assistant can:

- 📖 **read** a text file
- 📝 **summarize** a document
- 💡 **explain** a document in simple words
- ❓ **answer questions** about a document, using **only** what the document says

---

## 🤔 What Is Document AI?

A language model only knows what it learned during training. It has **never seen your files**: your notes, your project report, your company policy.

**Document AI** solves this in a simple way:

> **Read the file with Python → put its text inside the prompt → ask the model to work on it.**

The model doesn't "open" the file. **We** open it and **paste its content into the message**. The model just reads the text we give it.

### Why do we need it?

| Question | Model alone | With the document |
|----------|-------------|-------------------|
| "Who is on my project team?" | ❌ Doesn't know; may **make up** names | ✅ Reads `project.txt` → *Rahul, Anita, Vikram* |
| "Summarize my notes" | ❌ Has no notes | ✅ Summarizes the actual file |
| "What database did we use?" | ❌ Guesses | ✅ Answers *SQLite*, from the file |

### How does it work?

```
User: "ask project.txt Who are the team members?"
              │
              ▼
   Python reads data/project.txt          ← Day 5 file tool
              │
              ▼
   Build a prompt:
   ┌──────────────────────────────────┐
   │ Instructions (answer from doc)   │
   │ Document:  <file text here>      │
   │ Question:  Who are the team...?  │
   └──────────────────────────────────┘
              │
              ▼
        AI model reads it all
              │
              ▼
   "The team members are Rahul, Anita and Vikram."
```

This idea of putting real data into the prompt so the model answers from facts is called **grounding**. It's the foundation of **RAG**, explained at the end of this README.

---

## 🧩 The 3 Parts at a Glance

| Part | What we build | New / changed files |
|------|---------------|---------------------|
| **P1** | A **file reader tool** and a test, with no AI | `tools.py` (+ `read_text_file`), `test_file_tool.py`, `data/notes.txt` |
| **P2** | Send file content to the AI: **summarize** and **explain** commands | `assistant.py`, `data/project.txt` |
| **P3** | **Document Q&A**: ask questions, and the AI answers only from the file | `assistant.py` (+ `ask` command) |

Each part builds on the previous one. Day 4's tools (time, dice, password) and Tool Manager still work.

---

## 📁 Folder Structure

```
Day_05_Document-AI/
├── README.md
├── Day05_P1/
│   ├── tools.py              # Day 4 tools + read_text_file()
│   ├── test_file_tool.py     # test the file reader alone
│   └── data/
│       └── notes.txt         # sample document
├── Day05_P2/
│   ├── tools.py
│   ├── tool_manager.py       # from Day 4 (unchanged)
│   ├── test_file_tool.py
│   ├── assistant.py          # + summarize / explain
│   └── data/
│       ├── notes.txt
│       └── project.txt       # second sample document
└── Day05_P3/
    ├── tools.py
    ├── tool_manager.py
    ├── test_file_tool.py
    ├── assistant.py          # + ask (document Q&A)
    └── data/
        ├── notes.txt
        └── project.txt
```

> Setup (venv, `requirements.txt`, `.env`) is shared at the **project root**, the same as in previous days. No new packages are needed, because reading files is built into Python.

---

## ▶️ How to Run

> ⚠️ Run each script **from inside its own part folder**. The code uses the relative path `data/...`, so it looks for the `data` folder in the **current directory**.

```bash
cd Day_05_Document-AI/Day05_P1
python test_file_tool.py

cd ../Day05_P2
python assistant.py

cd ../Day05_P3
python assistant.py
```

### Commands inside the assistant

| Command | Part | Example |
|---------|------|---------|
| `summarize <file>` | P2, P3 | `summarize notes.txt` |
| `explain <file>` | P2, P3 | `explain project.txt` |
| `ask <file> <question>` | P3 | `ask project.txt Who are the team members?` |
| time / dice / password | P2, P3 | `what time is it?` (Day 4 tools) |
| anything else | P2, P3 | normal chat with the chosen role |
| `quit` | all | exit |

---

## 📄 Sample Documents

### `data/notes.txt` (P1, P2, P3)

```
Python is one of the most popular programming languages.

It is easy to learn.

Python is widely used in Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.

Python supports object-oriented programming
and has thousands of useful libraries.
```

### `data/project.txt` (P2, P3)

```
Project Name: Smart Library System

Project Duration:
January 2026 to June 2026

Programming Language:
Python

Database:
SQLite

Team Members:
Rahul
Anita
Vikram

The objective of the project was to automate
library management using Artificial Intelligence.
```

`project.txt` holds **private facts** that the model can't know (team names, dates, database). It's perfect for proving the AI really reads the file instead of guessing.

---

# Part 1 — Building the File Reader Tool 📖

**Goal:** write a Python function that reads a text file and returns its content, then test it alone **before** any AI is involved, just like the tools on Day 4.

### `tools.py`

The Day 4 tools are unchanged. One new tool, `read_text_file`, is added at the bottom.

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

def read_text_file(filename):

    try:

        with open(filename, "r") as file:

            return file.read()

    except FileNotFoundError:

        return "Error: File not found."
```

### Step-by-step explanation — `read_text_file`

```python
def read_text_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: File not found."
```

| Code | Meaning |
|------|---------|
| `def read_text_file(filename):` | The tool takes a file path, e.g. `"data/notes.txt"`. |
| `open(filename, "r")` | Opens the file in **read** mode (`"r"`). |
| `with ... as file:` | A **context manager**: it closes the file automatically when done, even if an error happens. |
| `file.read()` | Reads the **whole file** into one string. |
| `try: ... except FileNotFoundError:` | If the file doesn't exist, return a friendly message **instead of crashing** the program. |

> 💡 **Why `try/except`?** Users mistype file names. Without it, one typo (`notess.txt`) would crash the whole assistant. With it, the user just sees an error message and keeps chatting.

### `test_file_tool.py`

```python
from tools import read_text_file

text = read_text_file("data/notes.txt")

print(text)
```

Calls the tool on `data/notes.txt` and prints the content. There's no AI, so it runs instantly.

**Try the error case too:** change the name to a file that doesn't exist (e.g. `data/python.txt`) and run again. You should see `Error: File not found.` instead of a crash.

### 📤 Output — Part 1

#### `python test_file_tool.py` (file exists)
```
python test_file_tool.py 
Python is one of the most popular programming languages.

It is easy to learn.

Python is widely used in Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.

Python supports object-oriented programming
and has thousands of useful libraries.
(venv) 
```

#### File not found (wrong file name)
```
(paste output here)
```

**Observation:**
<!-- e.g. The file printed exactly as written; a wrong name shows the error instead of crashing. -->

---

# Part 2 — Sending File Content to the AI 🧠

**Goal:** let the user type `summarize <file>` or `explain <file>`. The assistant reads the file, puts its text into a prompt, and asks the AI.

**Same assistant, different documents:** one piece of code works for **any** file in `data/`. Change the file name and you get a different summary.

### `assistant.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

from tools import (
    get_current_time,
    roll_dice,
    generate_password,read_text_file)

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

    text = user_input.lower()

    if text.startswith("summarize "):
        filename = user_input[10:].strip()
        file_content = read_text_file(
        "data/" + filename
        )

        prompt = f"""
        Summarize the following document.

        Document:

        {file_content}
        """

        response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[

        {
            "role":"system",
            "content":"You are a helpful assistant."
        },

        {
            "role":"user",
            "content":prompt
        }

        ]

        )

        print(response.choices[0].message.content)
        continue

    if text.startswith("explain"):
        filename = user_input[8:].strip()
        file_content = read_text_file(
        "data/" + filename
        )

        prompt = f"""
        Explain the following document.

        Document:

        {file_content}
        """

        response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[

        {
            "role":"system",
            "content":"You are a helpful assistant."
        },

        {
            "role":"user",
            "content":prompt
        }

        ]

        )

        print(response.choices[0].message.content)
        continue

   
      

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

### Step-by-step explanation

**1. Imports, config, client, roles, menu: same as Day 4**

The only change is that `read_text_file` is now imported from `tools.py`.

**2. Detect the command**

```python
text = user_input.lower()

if text.startswith("summarize "):
    filename = user_input[10:].strip()
```

| Code | Meaning |
|------|---------|
| `text.startswith("summarize ")` | `True` if the message **begins with** `summarize ` (with a space). Unlike Day 4's `in`, this only matches at the **start**. |
| `user_input[10:]` | **Slicing**: skip the first 10 characters (`"summarize "` is 10 characters long) and keep the rest, which is the file name. |
| `.strip()` | Remove extra spaces before/after the name. |

`"summarize notes.txt"` → `filename = "notes.txt"`

**3. Read the file**

```python
file_content = read_text_file("data/" + filename)
```

Adds the folder in front: `"data/" + "notes.txt"` → `"data/notes.txt"`, then uses the P1 tool.

**4. Build the prompt with an f-string**

```python
prompt = f"""
Summarize the following document.

Document:

{file_content}
"""
```

| Piece | Meaning |
|-------|---------|
| `f""" ... """` | A **multi-line f-string**: text over many lines, with variables inside `{}`. |
| `Summarize the following document.` | The **instruction**: what we want. |
| `{file_content}` | Replaced by the **entire file text**. This is how the document "enters" the AI. |

**5. Send it to the model as a fresh, separate conversation**

```python
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": prompt}
    ]
)
print(response.choices[0].message.content)
continue
```

| Point | Meaning |
|-------|---------|
| New `messages=[...]` list | Document tasks **don't use** the chat history or the chosen role. Each request is a clean, one-off request. |
| `continue` | Skip the rest of the loop (Tool Manager and normal chat). |

**6. `explain` works exactly the same way**

```python
if text.startswith("explain"):
    filename = user_input[8:].strip()   # "explain " = 8 characters
```

Only two things change: the slice (`[8:]`) and the instruction (`Explain the following document.`).

**7. Everything else: Day 4 behaviour**

If the message isn't `summarize` or `explain`, it goes to the **Tool Manager** (time/dice/password) and then to **normal chat with memory**.

### Order of checks in the loop

```
input
  │
  ├─ starts with "summarize " → read file → AI summarizes → print
  ├─ starts with "explain"    → read file → AI explains   → print
  ├─ Tool Manager match?      → time / dice / password    → print
  └─ otherwise                → normal chat with memory   → print
```

### 📤 Output — Part 2

#### `summarize notes.txt`
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

Enter your choice : 3

You : summarize notes.txt
The document briefly summarizes the key points about Python, a popular programming language. It states that Python is:

* Easy to learn
* Widely used in several fields, including:
        + Artificial Intelligence
        + Machine Learning
        + Data Science
        + Automation
        + Web Development
* Supports object-oriented programming
* Has a vast collection of useful libraries

You : summarize project.txt
Here's a summary of the document:

The Smart Library System project is a Python-based automation system aimmin to manage libraries using Artificial Intelligence. The project aims to be completed within the timeframe of January 2026 to June 2026. The team members involved will be Rahul, Anita, and Vikram.

You : explain project.txt
This is a brief project overview document, likely used to summarize the details of a university or college project.

Here's a breakdown of the document's content:

1. **Project Name and Duration**: The document starts by stating the project name, "Smart Library System", and its duration, from January 2026 to June 2026. This indicates that the project is taking place over a specific period.

2. **Programming Language and Database**: It mentions that the project is written in Python and uses SQLite as the database. Python is a popular programming language used for various applications, including data analysis, machine learning, and automation. SQLite is a lightweight relational database that is easy to use and requires minimal setup.

3. **Team Members**: The document lists the team members responsible for the project, which are Rahul, Anita, and Vikram. This provides an opportunity to recognize and acknowledge their contributions to the project.

4. **Project Objective**: The primary objective of the project, as stated, is to automate library management using Artificial Intelligence (AI). The library management system is expected to utilize AI to streamline various library-related tasks, such as tracking book inventory, recommending books to users, and facilitating online access to library resources.

In summary, this document provides an overview of the Smart Library System project, including its duration, programming language, database, and team members. It highlights the use of AI to automate library management tasks,making it a cutting-edge initiative in the field of library science.

You : quit

AI  : Goodbye! Have a great day.
(venv) 
```

**Observation:**
<!-- e.g. Same code, different files → completely different answers based on each document. -->

---

# Part 3 — Document Q&A Assistant ❓

**Goal:** ask **specific questions** about a document:

```
ask project.txt Who are the team members?
ask project.txt Which database was used?
ask notes.txt   What is Python used for?
```

…and make the AI answer **only from the document**, and admit when the answer isn't there.

### `assistant.py`

Same as P2, plus a new `ask` block before the Tool Manager.

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

from tools import (
    get_current_time,
    roll_dice,
    generate_password,read_text_file)

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

    text = user_input.lower()

    if text.startswith("summarize "):
        filename = user_input[10:].strip()
        file_content = read_text_file(
        "data/" + filename
        )

        prompt = f"""
        Summarize the following document.

        Document:

        {file_content}
        """

        response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[

        {
            "role":"system",
            "content":"You are a helpful assistant."
        },

        {
            "role":"user",
            "content":prompt
        }

        ]

        )

        print(response.choices[0].message.content)
        continue

    if text.startswith("explain"):
        filename = user_input[8:].strip()
        file_content = read_text_file(
        "data/" + filename
        )

        prompt = f"""
        Explain the following document.

        Document:

        {file_content}
        """

        response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[

        {
            "role":"system",
            "content":"You are a helpful assistant."
        },

        {
            "role":"user",
            "content":prompt
        }

        ]

        )

        print(response.choices[0].message.content)
        continue


    
    if text.startswith("ask"):
        parts = user_input.split(maxsplit=2)
        #print(parts)
        filename = parts[1]
        question = parts[2]

        file_content = read_text_file(
        "data/" + filename
        )

        prompt = f"""
You are given a document.

Answer the user's question using
only the information present
in the document.

If the answer is not available,
say:
'I couldn't find that information
in the document.'

Document:

{file_content}

Question:

{question}
"""



        response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[

        {
            "role":"system",
            "content":"You are a helpful assistant."
        },

        {
            "role":"user",
            "content":prompt
        }

        ]

        )

        print(response.choices[0].message.content)
        continue


    

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

### Step-by-step explanation (new `ask` block)

**1. Split the command into 3 parts**

```python
if text.startswith("ask"):
    parts = user_input.split(maxsplit=2)
    filename = parts[1]
    question = parts[2]
```

`split(maxsplit=2)` splits on spaces, but **only at the first 2 spaces**, so the question stays in one piece:

```
"ask project.txt Who are the team members?"
        │
        ▼  split(maxsplit=2)
["ask", "project.txt", "Who are the team members?"]
  [0]        [1]                  [2]
```

| Variable | Value |
|----------|-------|
| `parts[1]` → `filename` | `"project.txt"` |
| `parts[2]` → `question` | `"Who are the team members?"` |

Without `maxsplit=2`, the question would be cut into separate words.

**2. Read the file**: same as P2.

**3. The grounding prompt (the most important part of Day 5)**

```
You are given a document.

Answer the user's question using
only the information present
in the document.

If the answer is not available,
say:
'I couldn't find that information
in the document.'

Document:
{file_content}

Question:
{question}
```

| Prompt piece | Why it's there |
|--------------|----------------|
| *"using only the information present in the document"* | Stops the model from mixing in its own general knowledge. |
| *"If the answer is not available, say: 'I couldn't find…'"* | Gives the model a **safe way out**, so it doesn't **invent** (hallucinate) an answer. |
| `Document:` then `Question:` | Clear labels, so the model knows which text is the source and which is the question. |

> 🧪 **Best test:** ask something **not** in the file, e.g. `ask project.txt What was the budget?`. A well-grounded assistant says *"I couldn't find that information in the document."* and doesn't make up a number.

**4. Send and print**: same as P2, then `continue`.

### Order of checks in the loop (P3)

```
input
  ├─ "summarize " → summarize file
  ├─ "explain"    → explain file
  ├─ "ask"        → answer question from file   ← NEW
  ├─ Tool Manager → time / dice / password
  └─ otherwise    → normal chat with memory
```

### 📤 Output — Part 3

#### `ask project.txt Who are the team members?`
```
 python assistant.py 
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

You : ask project.txt Who are the team members?
The team members for the Smart Library System project are:

1. Rahul
2. Anita
3. Vikram

You : 
```

#### `ask project.txt Which database was used?`
```
You : ask project.txt Which database was used?
The database used was SQLite
```

#### `ask notes.txt What is Python used for?`
```
You : ask notes.txt What is Python used for?`
Python is widely used in Artificial Intelligence, Machine Learning, Data Science, Automation, and Web Development.

```

#### Answer NOT in the document — `ask project.txt What was the budget?`
```
You : ask project.txt What was the budget?
I couldn't find that information in the document.
```

**Observation:**
<!-- e.g. Correct answers from the file; for the budget it said it couldn't find the information instead of guessing. -->

---

## 🔍 P1 → P3 Comparison

| | P1 | P2 | P3 |
|---|----|----|----|
| Read a file | ✅ | ✅ | ✅ |
| AI involved | ❌ | ✅ | ✅ |
| Summarize / Explain | ❌ | ✅ | ✅ |
| Ask questions about a file | ❌ | ❌ | ✅ |
| Answers restricted to the document | — | ❌ | ✅ |
| Day 4 tools + normal chat | — | ✅ | ✅ |

---

## 🧠 Why We Need RAG

Day 5 sends the **entire file** to the model every time. That works for small files like `notes.txt`, but it breaks down for real documents:

| Problem | Why |
|---------|-----|
| 📏 **Context limit** | Every model has a maximum input size (its *context window*). A 300-page PDF won't fit. |
| 🐢 **Slow** | More text means more processing on every question. |
| 💸 **Costly** | With paid APIs, you pay per token, so sending the whole document every time is expensive. |
| 🎯 **Less accurate** | The answer is buried in lots of irrelevant text, and models can miss it. |
| 📚 **Many documents** | You can't paste 1,000 files into one prompt. |

**RAG (Retrieval-Augmented Generation)** fixes this:

```
Day 5 (now):   whole document  ─────────────► prompt ─► AI

RAG:           documents ─► split into small chunks ─► store
               question  ─► find the few MOST relevant chunks
                                   │
                                   ▼
                    only those chunks ─► prompt ─► AI
```

| Word | Meaning |
|------|---------|
| **Retrieval** | Find the relevant pieces of the documents. |
| **Augmented** | Add those pieces to the prompt. |
| **Generation** | The model writes the answer from them. |

The **grounding prompt** you wrote in P3 (*"answer only from the document"*) stays exactly the same in RAG. RAG just changes **what** text goes into the `Document:` part.

---

## ⚠️ Known Limitations / Improvements

1. **`explain` and `ask` catch normal questions.** The checks are `startswith("explain")` and `startswith("ask")` with **no space**, so:
   - `explain recursion` (a normal question to the Teacher role) is treated as a file named `recursion` → "File not found" is sent to the AI.
   - `asking for help…` is treated as an `ask` command.

   Fix: use `startswith("explain ")` and `startswith("ask ")`, like `summarize `.
2. **`ask` can crash.** `ask notes.txt` (no question) or just `ask` → `parts[2]` doesn't exist → **IndexError** crashes the program. Fix: check `len(parts) < 3` first and show a usage message.
3. **Error text is sent to the AI.** If the file isn't found, the string `"Error: File not found."` is placed in the prompt as if it were the document. Fix: check for the error and print it directly instead of calling the AI.
4. **Encoding on Windows.** `open(filename, "r")` uses the system encoding. Files with Bangla text, emojis or special characters can raise `UnicodeDecodeError`. Fix: `open(filename, "r", encoding="utf-8")`.
5. **`test_file_tool.py` in P2/P3 reads `data/python.txt`**, which doesn't exist, so it prints `Error: File not found.` Change it to `data/notes.txt` (or use it on purpose to test the error case).
6. **The same API-call code is repeated 3 times** (summarize, explain, ask). Move it into one helper function, e.g. `ask_ai(prompt)`.
7. **Document answers aren't saved to memory**, and they ignore the chosen role. A follow-up like "explain that more simply" won't know what "that" was.
8. **Must run from the part folder** because of the relative path `data/`. Fix: build the path from the script's location with `os.path.dirname(__file__)`.
9. **`__pycache__/` folders** are created automatically by Python. Add `__pycache__/` to `.gitignore`.

---

## ✅ Key Takeaways

- A model can't read your files. **Python reads them and puts the text in the prompt.**
- **Test the file tool alone first** (P1), then connect it to the AI.
- `startswith()`, slicing and `split(maxsplit=2)` turn a typed command into a file name and a question.
- One assistant can summarize, explain and answer questions about **any** document. Only the file changes.
- **Grounding prompts** ("use only the document; say so if not found") reduce made-up answers.
- Sending whole files doesn't scale. That's why the next step is **RAG**.

---

## ➡️ Next: Day 06
<!-- add next topic -->