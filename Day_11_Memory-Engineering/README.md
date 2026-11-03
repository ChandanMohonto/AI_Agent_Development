# Day 11 — Memory Engineering: Teach Your AI Agent to Remember 🧠💾

Part of the **AI_Agent_Journy** day-by-day learning series.

| Day | Topic |
|-----|-------|
| Day 01 | Ollama chatbot |
| Day 02 | AI assistant with memory (in RAM, lost on exit) |
| Day 03 | Prompt engineering — system prompts & roles |
| Day 04 | AI tools — keyword-based tool selection |
| Day 05 | Document AI — read, summarize, explain and question files |
| Day 06 | RAG — embeddings + cosine similarity |
| Day 07 | AI planner — the model chooses the tool |
| Day 08 | MCP — tools in a server, discovered at runtime |
| Day 09 | Autonomous agent — loop until done |
| Day 10 | Advanced planning — task decomposition |
| **Day 11** | **Memory engineering — persistent, searchable, intelligent long-term memory** |

---

## 🎯 Goal of Day 11

Our Day 10 agent is smart, but it has **amnesia**. 😶

```
Run 1:  You : My name is Chandan.
        AI  : Nice to meet you, Chandan!
        (program closes)

Run 2:  You : What is my name?
        AI  : I don't know your name.      ❌
```

On **Day 2** the agent remembered within one session, but the memory was a Python list in **RAM**, so it was **gone as soon as the program closed**.

On **Day 11** the agent gets a **long-term memory** that:

- 💾 is **saved to disk** (SQLite database), so it survives restarts
- 🔎 is **searched by meaning** (embeddings, like Day 6 RAG), so only relevant memories are recalled
- 🧠 **extracts the important facts** ("The user's name is Chandan") instead of storing every message

```
Run 2:  You : What is my name?
        (agent recalls: "The user's name is Chandan.")
        AI  : Your name is Chandan.        ✅
```

---

## 🤔 What Is Memory Engineering?

**Memory engineering** is designing **what** an AI agent remembers, **where** it stores it, **how** it finds it again, and **what it forgets**.

An LLM by itself remembers **nothing** between calls (we learned this on Day 2). Every bit of "memory" an AI app has is **built by engineers around the model**:

```
          ┌────────── what to SAVE? ──────────┐
          │                                   │
 conversation ──► memory extractor ──► long-term memory (SQLite)
                                              │
 new question ──► search by meaning ◄─────────┘
                        │
                        ▼
          relevant memories ──► added to the prompt ──► LLM answers
```

### The types of memory (and where they live in our agent)

| Memory type | Human example | In our agent | Day |
|-------------|---------------|--------------|-----|
| ⚡ **Short-term / working memory** | Remembering a phone number just long enough to dial it | The **agent state** (tasks, observations); lost after the run | Days 9–10 |
| 💬 **Conversation memory** | Remembering what was said earlier in **this** chat | `messages` list in RAM | Day 2 |
| 📼 **Episodic memory** (long-term) | "Last Tuesday I talked to Rahul about the trip" | Every **conversation** saved to SQLite: `save_memory()` | **Day 11 P2** |
| 📚 **Semantic memory** (long-term) | "Rahul is vegetarian," a **fact**, without remembering when you learned it | Only **useful facts**, extracted by the LLM: `save_semantic_memory()` | **Day 11 P3** |
| 🛠️ Procedural memory | Knowing *how* to ride a bike | Prompts and code (how the agent works) | all days |

---

## 🧑‍🍳 Real-Life Scenario: The Café That Remembers You

**Café A (no memory, our Day 10 agent):**
Every morning: *"Hi! What would you like?"* You explain again: oat milk, no sugar, a large flat white. Every. Single. Day. 😩

**Café B (episodic memory, Day 11 P2):**
The barista keeps a notebook of **every conversation** with you. Before serving, they flip through it to find the relevant pages. It works, but the notebook fills up with *"nice weather today"* and *"what time do you close?"*

**Café C (semantic memory, Day 11 P3):**
The barista keeps a small card with **just the facts**:

```
📇 Chandan
   • oat milk, no sugar
   • large flat white
   • allergic to nuts
```

When you walk in, they glance at the card: *"The usual, Chandan?"* ☕ Small, fast, useful, and they **didn't write down** "asked what time we close", because that's not worth remembering.

**Café C is the Day 11 agent.** The memory extractor decides what goes on the card.

### 🧪 Real-life scenario 2: a QA assistant that remembers your project

```
Week 1:  "Our app uses Playwright with TypeScript, and staging is at stage.myapp.com."
         → remembered: "Project uses Playwright + TypeScript; staging URL is stage.myapp.com"

Week 3:  "Write a login test."
         → recalls the project facts → writes a Playwright TypeScript test against staging
           without you repeating anything.
```

### Where you already see this

| Product | Memory feature |
|---------|----------------|
| ChatGPT / Claude / Gemini | "Memory" settings that remember your preferences across chats |
| Customer support bots | Remember your past tickets and orders |
| Coding assistants | Remember project conventions and past decisions |
| Personal assistants | Remember your schedule habits, contacts and preferences |
| E-commerce | "Customers like you…", remembering sizes and favourite brands |

---

## ✅ Why We Need It (Benefits)

| Benefit | Explanation |
|---------|-------------|
| 🔁 **Continuity** | The user doesn't repeat themselves every session. |
| 🎯 **Personalisation** | Answers fit **this** user (name, skills, goals, preferences). |
| 💾 **Survives restarts** | SQLite is a file on disk, so memory outlives the program. |
| 🔎 **Recall by meaning** | "What's my name?" finds "My name is Chandan" with no keyword match needed (Day 6 embeddings). |
| 📏 **Fits the context window** | Only the **top 3 relevant** memories go into the prompt, not the whole history. |
| 🧠 **Smart filtering** | The extractor keeps facts and drops noise (current time, one-off questions). |
| 🧩 **Works with the whole agent** | The planner, tools and answer generator all see the recalled memories. |

## ⚠️ Limitations

| Limitation | Explanation |
|------------|-------------|
| 🔐 **Privacy** | The agent stores personal information. Users must know, be able to see it, and be able to **delete** it. Never store passwords or sensitive data. |
| 🤥 **Wrong memories** | If the extractor mis-reads a conversation, a **false fact** is saved and reused confidently. |
| 🕰️ **Stale memories** | "I live in Delhi" stays forever, even after you move. There's no updating or expiry. |
| 📑 **Duplicates** | The same fact can be saved again and again (we saw this in testing). |
| 🎯 **Noisy recall** | A low similarity threshold (0.20) means unrelated memories also get recalled. |
| 🐢 **Doesn't scale** | Every search loads **all** rows and compares them one by one. Fine for 100, slow for 1,000,000. Real systems use vector databases. |
| 💸 **More LLM calls** | Every request does embedding + search + extraction. |
| 🧨 **Memory poisoning** | A user (or a document) can plant instructions as "facts" that change future behaviour. |

---

## 🧩 The 4 Parts at a Glance

| Part | Course lessons | What we build | New / changed files |
|------|----------------|---------------|---------------------|
| **P1** | 134–136 | **Persistent memory with SQLite**: save, embed and search memories, tested alone | `memory.py`, `test_memory.py` |
| **P2** | 137–139 | **Memory in the agent**: recall before planning, save after answering (episodic) | `state.py`, `task_planner.py`, `planner.py`, `answer.py`, `loop.py`, `runner.py` |
| **P3** | 140–141 | **Memory extractor**: an LLM decides what's worth remembering | `memory_extractor.py`, `test_memory_extractor.py`, `memory.py` (+ `save_semantic_memory`) |
| **P4** | 142–144 | **Final integration**: semantic memory in the complete agent | *Identical to P3.* P4 is the final test run of the same code |

> ℹ️ The course zips for P3 and P4 contain **byte-for-byte identical** code. The difference between lessons 140–141 and 142–143 is testing, not new code. This README explains the code once, under P3.

---

## 📁 Folder Structure

```
Day_11_Memory-Engineering/
├── README.md
├── Day11_P1/
│   ├── memory.py               # SQLite memory: save, embed, search
│   └── test_memory.py          # test memory alone
├── Day11_P2/
│   ├── memory.py               # same as P1
│   ├── test_memory.py
│   ├── state.py                # + "memories"
│   ├── task_planner.py         # + "no tasks" rule
│   ├── planner.py              # + sees memories
│   ├── answer.py               # + uses memories
│   ├── loop.py                 # recall → plan → act → answer → save
│   ├── executor.py             # from Day 10
│   ├── runner.py               # ▶️ START HERE (+ create_database)
│   ├── server.py               # from Day 8
│   └── mcp_client.py           # from Day 8 (in-memory)
├── Day11_P3/
│   ├── (all P2 files)
│   ├── memory.py               # + save_semantic_memory()
│   ├── memory_extractor.py     # NEW: decides what to remember
│   ├── test_memory_extractor.py
│   └── loop.py                 # + extract & save facts
└── Day11_P4/                   # identical to P3
```

### How the files connect

```
runner.py
 ├── memory.py → create_database()
 └── loop.py → run_agent_loop()
      ├── memory.py → search_semantic_memories()   ① RECALL
      ├── state.py  → add_memory()
      ├── task_planner.py → decompose_task()        ② PLAN
      ├── planner.py / executor.py (MCP)            ③ ACT
      ├── answer.py → format_answer()               ④ ANSWER
      ├── memory.py → save_memory()                 ⑤ SAVE conversation
      └── memory_extractor.py → extract_memory()    ⑥ EXTRACT fact (P3)
           └── memory.py → save_semantic_memory()
```

---

## 🔧 Changes from the Course Files

The Day 11 course files are built on the **original** Day 10 code, so they bring back every bug we fixed on Days 8 and 10, plus some new memory bugs. **The code in this README is the fixed version**, with each change marked `# FIX:`.

### ⚠️ First: delete the shipped `memory.db`!

The zips include `memory.db` files **already filled with the course author's test memories** ("My name is Pankaj.", 3–11 rows per part). If you keep them, **your agent will think your name is Pankaj.** 😄

```bash
rm -f Day_11_Memory-Engineering/Day11_P*/memory.db
```

A new, empty database is created automatically on the first run.

### All fixes

| File | Problem in the course version | Fix | From |
|------|-------------------------------|-----|------|
| `server.py` | `print()` to stdout breaks MCP stdio | Print to `stderr` | Day 8 |
| `mcp_client.py` | stdio `Connection closed` on this PC | In-memory `Client(mcp)` | Day 8 |
| `executor.py` | No-tool task or wrong tool name → `ToolError` crash | `TOOL: none` path + `try/except` | Day 10 |
| `planner.py` | No rule for tasks without a tool | Rule 7b `TOOL: none`, `temperature=0` | Day 10 |
| `task_planner.py` | Bullets, numbers and `<think>` become fake tasks | Cleaned, `temperature=0` | Day 10 |
| `task_planner.py` | 🆕 The new rule makes the model return `NONE`, which was added as **a task called "NONE"** | `NONE` is skipped, so the task list stays empty | Day 11 |
| `loop.py` | 🆕 An empty task list wasn't handled (`all_tasks_completed()` is `False` for no tasks, so the planner is asked anyway) | No tasks → answer directly | Day 11 |
| `loop.py` | 🆕 Memory was saved **only** when the planner said `FINISH`. When the code-level check finished the run (all tasks completed), **nothing was saved** | Memory is saved in **one place**, after every run | Day 11 |
| `loop.py` | `max_steps` → empty answer; dirty tool names | Safety-net answer, cleaned names, `max_steps=8` | Day 10 |
| `memory_extractor.py` | 🆕 `fact != "NONE"` is exact, so `NONE.`, `None` or `<think>…` got **saved as facts** | Normalised to `NONE`, `temperature=0` | Day 11 |
| `answer.py` | The LLM may invent or hide values | Fact rules + "only use clearly relevant memories" | Day 10 + 11 |

> ✅ The fixed P3 flow was tested with fake LLM replies and a temporary database:
> run 1 *"My name is Chandan."* → no tasks → fact *"The user's name is Chandan."* saved;
> run 2 *"What time is it?"* → tool task → **no** fact saved (`NONE`);
> run 3 *"What is my name?"* → the name memories were recalled with the **highest** scores.
> The test also showed two real limitations: **duplicate facts** and **noisy recall** at threshold 0.20.

---

## ⚙️ Setup

Day 11 needs the **embedding model** and **`numpy`** from Day 6 (memory search uses embeddings).

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
which python                               # must show .../AI_Agent_Journy/venv/Scripts/python

ollama pull nomic-embed-text               # if not already done on Day 6
python -m pip install -r requirements.txt  # openai, python-dotenv, numpy, fastmcp<3

rm -f Day_11_Memory-Engineering/Day11_P*/.env        # use the shared root .env
rm -f Day_11_Memory-Engineering/Day11_P*/memory.db   # remove the course author's memories
```

> **SQLite needs no install.** `sqlite3` is built into Python, and the database is a single file (`memory.db`) created in the folder you run from.
>
> **Model tip:** use **`llama3.2`** in the root `.env`. The zip's `qwen3:1.7b` is too small for the strict formats.

---

## ▶️ How to Run: Which File First?

> Run each script from **inside its part folder**. `memory.db` is created in the **current folder**, so each part has its own memory.

| # | Folder | Command | What it does | Expected |
|---|--------|---------|--------------|----------|
| 1 | `Day11_P1` | `python test_memory.py` | Save 3 memories, search "What is my name" | The name memory has the **highest score** |
| 2 | `Day11_P2` | `python runner.py` (run it **twice**) | Run 1: introduce yourself. Run 2: ask your name | Run 2 recalls your name ✅ |
| 3 | `Day11_P3` | `python test_memory_extractor.py` | Extract a fact from a "current time" chat | `NONE` (nothing worth remembering) |
| 4 | `Day11_P3` | `python runner.py` (run it **several** times) | Introduce yourself, ask a tool question, ask your name | `Memory Extracted:` shows a fact or `NONE` |
| 5 | `Day11_P4` | same as #4 | Final test (same code) | Same as #4 |

```bash
cd "/d/AI Agents/AI_Agent_Journy/Day_11_Memory-Engineering/Day11_P1"
python test_memory.py

cd ../Day11_P2
python runner.py        # User : My name is Chandan and I am a QA engineer.
python runner.py        # User : What is my name?

cd ../Day11_P3
python test_memory_extractor.py
python runner.py        # User : I am learning AI agents with Python.
python runner.py        # User : What time is it?
python runner.py        # User : What am I learning?
```

### 🔍 See what's stored

The database is just a file, so you can look inside:

```bash
python -c "import sqlite3; [print(r) for r in sqlite3.connect('memory.db').execute('SELECT id, user_message, assistant_message, created_at FROM memories')]"
```

**Reset memory** (start fresh): `rm memory.db`

---

# Part 1 — Persistent Memory with SQLite 💾

**Goal:** store memories in a **database file**, with an **embedding** for each, and find them again **by meaning**. Tested alone, with no agent.

### What is SQLite?

**SQLite** is a small database that lives in **one file** (`memory.db`). There's no server and no install, and it's built into Python. It stores data in **tables** (rows and columns), like a spreadsheet you query with **SQL**.

Our table:

| id | user_message | assistant_message | embedding | created_at |
|----|--------------|-------------------|-----------|------------|
| 1 | My name is Chandan. | Nice to meet you, Chandan. | `[0.02, -0.41, …]` (768 numbers as text) | 2026-11-03 10:15:00 |
| 2 | I am learning Python. | Python is useful for AI… | `[…]` | 2026-11-03 10:16:12 |

## `memory.py`

```python
import json
import sqlite3

import numpy as np
from openai import OpenAI


DATABASE = "memory.db"


embedding_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            assistant_message TEXT,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def create_embedding(text):
    response = embedding_client.embeddings.create(
        model="nomic-embed-text",
        input=text
    )
    
    return response.data[0].embedding


def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    return np.dot(v1, v2) / (
        np.linalg.norm(v1) *
        np.linalg.norm(v2)
    )


def save_memory(user_message, assistant_message):
    text = user_message + "\n" + assistant_message

    embedding = create_embedding(text)
    

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (
            user_message,
            assistant_message,
            embedding
        )
        VALUES (?, ?, ?)
        """,
        (
            user_message,
            assistant_message,
            json.dumps(embedding)
        )
    )

    connection.commit()
    connection.close()


def search_semantic_memories(
    query,
    top_k=3,
    threshold=0.20
):
    query_embedding = create_embedding(query)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_message,
            assistant_message,
            embedding,
            created_at
        FROM memories
    """)

    rows = cursor.fetchall()

    connection.close()

    results = []

    for (
        user_message,
        assistant_message,
        embedding_json,
        created_at
    ) in rows:

        memory_embedding = json.loads(
            embedding_json
        )

        score = cosine_similarity(
            query_embedding,
            memory_embedding
        )
        
        if score >= threshold:
            results.append({
                "user_message": user_message,
                "assistant_message": assistant_message,
                "created_at": created_at,
                "score": score
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    #print(results)

    return results[:top_k]
```

### Step-by-step explanation

**Setup**

| Code | Meaning |
|------|---------|
| `import sqlite3` | Python's built-in SQLite library. |
| `import json` | To turn the embedding **list** into **text** for storage, and back. |
| `DATABASE = "memory.db"` | The database file name, created in the current folder. |
| `embedding_client = OpenAI(base_url="http://localhost:11434/v1", …)` | Ollama client for embeddings (Day 6). |

**`create_database()`**

| Code | Meaning |
|------|---------|
| `sqlite3.connect(DATABASE)` | Open the file, creating it if it doesn't exist. |
| `cursor = connection.cursor()` | A **cursor** sends SQL commands. |
| `CREATE TABLE IF NOT EXISTS memories (...)` | Make the table **only the first time**. Safe to call on every start. |
| `id INTEGER PRIMARY KEY AUTOINCREMENT` | A unique number for each row, given automatically (1, 2, 3…). |
| `user_message TEXT` / `assistant_message TEXT` | The conversation. |
| `embedding TEXT` | The vector, stored as a JSON string. |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | The time is filled in automatically. |
| `connection.commit()` | **Save** the change to disk. Without it, nothing is written. |
| `connection.close()` | Release the file. |

**`create_embedding(text)`** and **`cosine_similarity(v1, v2)`**: exactly the Day 6 functions. Text becomes 768 numbers, and two vectors give a similarity score (≈1 means the same meaning).

**`save_memory(user_message, assistant_message)`**

| Code | Meaning |
|------|---------|
| `text = user_message + "\n" + assistant_message` | Embed the **whole exchange**, so the meaning of both sides is captured. |
| `embedding = create_embedding(text)` | Text → vector. |
| `INSERT INTO memories (...) VALUES (?, ?, ?)` | Add a row. |
| `?` placeholders + the tuple `(user_message, assistant_message, json.dumps(embedding))` | **Parameterised query**: SQLite inserts the values safely. Never build SQL by joining strings, because that allows **SQL injection**. |
| `json.dumps(embedding)` | List → text like `"[0.02, -0.41, ...]"`. |

**`search_semantic_memories(query, top_k=3, threshold=0.20)`**: semantic search over memory (Day 6 RAG, applied to memories)

| Step | Code | Meaning |
|------|------|---------|
| 1 | `create_embedding(query)` | Question → vector. |
| 2 | `SELECT user_message, assistant_message, embedding, created_at FROM memories` | Load **all** memories. |
| 3 | `json.loads(embedding_json)` | Text → list again. |
| 4 | `cosine_similarity(query_embedding, memory_embedding)` | Score each memory. |
| 5 | `if score >= threshold:` | Keep only memories that are similar enough. |
| 6 | `results.sort(key=lambda item: item["score"], reverse=True)` | Highest score first. `lambda item: item["score"]` means "sort by the score field". |
| 7 | `return results[:top_k]` | The best 3. |

> ⚠️ **`threshold=0.20` is very low.** Embedding scores between unrelated sentences are often 0.3–0.5, so almost everything passes. Look at the scores in your own output and raise it (e.g. 0.5) if unrelated memories show up.

## `test_memory.py`

```python
from memory import (
    create_database,
    save_memory,
    search_semantic_memories
)


create_database()

save_memory(
    "My name is Pankaj.",
    "Nice to meet you, Pankaj."
)

save_memory(
    "I am learning Python.",
    "Python is useful for AI development."
)

save_memory(
    "I am learning about MCP.",
    "MCP allows AI applications to use tools."
)


results = search_semantic_memories(
    "What is my name"
)

print("\nRelevant Memories")
print("-----------------")

for result in results:
    print("\nScore:", result["score"])
    print("User:", result["user_message"])
    print("Assistant:", result["assistant_message"])
```

| Code | Meaning |
|------|---------|
| `create_database()` | Make the table (if needed). |
| 3 × `save_memory(...)` | Save 3 sample conversations. |
| `search_semantic_memories("What is my name")` | Search by meaning. |
| loop + print | Show the score and text of each match. |

**Note:** every run **adds the 3 memories again**, so run it 3 times and you'll have 9 rows with duplicates. Delete `memory.db` to reset.

**Try it:** change the names to your own, and search `"What am I studying?"`. The Python memory should score highest, **even though no word matches**.

### 📤 Output — Part 1

#### `python test_memory.py`
```
$ python test_memory.py

Relevant Memories
-----------------

Score: 0.5421781557399292
User: My name is Pankaj.
Assistant: Nice to meet you, Pankaj.

Score: 0.5421781557399292
User: My name is Pankaj.
Assistant: Nice to meet you, Pankaj.

Score: 0.3413988581069373
User: I am learning Python.
Assistant: Python is useful for AI development.
(venv) 
```

**Observation:**
<!-- e.g. "My name is ..." scored highest for "What is my name" — found by meaning. -->

---

# Part 2 — Integrating Memory into the Agent 🤖💬

**Goal:** the Day 10 agent now **recalls** relevant memories before planning and **saves** every conversation after answering. This is **episodic memory**.

### The new agent flow

```
User request
   │
   ① RECALL   search_semantic_memories(request) → state["memories"]
   │
   ② PLAN     decompose_task()  → tasks  (or NO tasks for greetings / memory questions)
   │
   ③ ACT      planner → executor (MCP) → tick tasks   (skipped if no tasks)
   │
   ④ ANSWER   format_answer(state)  ← uses observations AND memories
   │
   ⑤ SAVE     save_memory(request, answer)   → memory.db
```

## `state.py`: + memories

```python
def create_state(user_request, max_steps=5):

    return {
        "user_request": user_request,
        "tasks": [],
        "current_task": None,
        "current_step": 0,
        "max_steps": max_steps,
        "actions": [],
        "observations": [],
        "results": [],
        "memories": [],
        "finished": False,
        "final_answer": ""
    }

def add_memory(state, memory):
    state["memories"].append(memory)

def add_task(state, task):

    state["tasks"].append({
        "task": task,
        "status": "pending"
    })


def complete_task(state, task):

    # Normalize the task received from the planner.
    # This makes the comparison tolerant of:
    # "Generate password"
    # "generate password"
    # "generate_password"

    normalized_task = (
        task
        .strip()
        .lower()
        .replace("_", " ")
    )

    for item in state["tasks"]:

        normalized_existing_task = (
            item["task"]
            .strip()
            .lower()
            .replace("_", " ")
        )

        if normalized_existing_task == normalized_task:

            item["status"] = "completed"

            return True

    return False


def add_action(state, action):

    state["actions"].append(action)


def record_observation(
    state,
    action,
    observation
):

    state["observations"].append({
        "step": state["current_step"],
        "action": action,
        "observation": observation
    })


def add_result(state, result):

    state["results"].append(result)


def get_pending_tasks(state):

    return [
        item["task"]
        for item in state["tasks"]
        if item["status"] == "pending"
    ]


def all_tasks_completed(state):

    if not state["tasks"]:
        return False

    return all(
        item["status"] == "completed"
        for item in state["tasks"]
    )


def next_step(state):

    state["current_step"] += 1


def can_continue(state):

    return (
        not state["finished"]
        and state["current_step"] < state["max_steps"]
    )


def finish(state, answer):

    state["final_answer"] = answer
    state["finished"] = True
```

| New | Meaning |
|-----|---------|
| `"memories": []` | Memories recalled for **this** request (each is a dict: `user_message`, `assistant_message`, `created_at`, `score`). |
| `add_memory(state, memory)` | Append one recalled memory. |

Everything else is the same as Day 10 (tasks with status, actions, observations, results, the step brake, finish).

## `task_planner.py`: + the "no tasks" rule

```python
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

CRITICAL RULE:

Return NO tasks (or "NONE") if the user request belongs to any of the following categories:
   1. Greetings or casual conversation (e.g., "hi", "hello", "how are you?")
   2. Introductions or personal details (e.g., "my name is Pankaj", "I live in Delhi")
   3. Memory questions about past interactions (e.g., "what is my name?", "what did we discuss earlier?")
   4. General knowledge/Q&A questions that can be answered directly without tools (e.g., "what is Machine Learning?", "explain gravity")


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

        # FIX: "NONE" means "no tasks", not a task called NONE
        if line.upper().strip(" .") == "NONE":
            continue

        if line:
            tasks.append(line)

    return tasks
```

| New | Meaning |
|-----|---------|
| `CRITICAL RULE: Return NO tasks (or "NONE")` for greetings, introductions, memory questions and general knowledge | These need **no tools**. Memory + LLM can answer directly, so it's faster and cheaper. |
| `if line.upper().strip(" .") == "NONE": continue` | **FIX:** the course version added `"NONE"` **as a task**, which the planner then tried to execute. Now it means an empty task list. |

| Request | Tasks |
|---------|-------|
| `My name is Chandan.` | *(none)* → answered directly, conversation saved |
| `What is my name?` | *(none)* → answered from **memory** |
| `What time is it?` | `Get the current time` |
| `Generate a password and explain Python.` | `Generate a secure password`, `Explain Python` |

The rest is the same as Day 10 (with the cleaning and `temperature=0` fixes).

## `planner.py`: + sees memories

```python
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def build_tool_descriptions(tools):

    descriptions = ""

    for tool in tools:

        descriptions += f"""
Tool:
{tool.name}

Description:
{tool.description}

----------------------------
"""

    return descriptions


def planner(state, tools):

    tool_descriptions = build_tool_descriptions(tools)

    prompt = f"""
You are an AI planner.

Your job is to select the next unfinished task
and the best tool to complete it.

User Request:

{state["user_request"]}

Relevant Previous Memories:
{state["memories"]}


Tasks:

{state["tasks"]}

Pending Tasks:

{[
    item["task"]
    for item in state["tasks"]
    if item["status"] == "pending"
]}

Completed Actions:

{state["actions"]}

Observations:

{state["observations"]}

Intermediate Results:

{state["results"]}

Available Tools:

{tool_descriptions}

Rules:

1. Select only ONE pending task.

2. The TASK must be copied EXACTLY from the
   pending task list.

3. Do not change the task wording.

4. Do not select a completed task.

5. Select the best available tool for that task.

6. Use previous observations and results, and relevant memories.

7. If an action failed, reconsider the task.

7b. If NO tool fits the task (for example
    "explain something"), use:  TOOL: none

8. If there are no pending tasks,
   return ONLY the word:

FINISH

9. If tasks are still pending, return exactly
   two lines in this format:

TASK: <exact pending task>
TOOL: <tool_name>

10. Do not explain anything.
11. IF the request can be answered directly using conversational memory, standard knowledge, or if tasks list is empty/NONE, respond ONLY with: FINISH

Next Decision:
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,  # FIX: more consistent decisions
        messages=[
            {
                "role": "system",
                "content": "You are an AI planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
```

| New | Meaning |
|-----|---------|
| `Relevant Previous Memories: {state["memories"]}` | The planner sees what the user said before. |
| Rule 6 `…and relevant memories.` | Use them when deciding. |
| Rule 11 `IF the request can be answered directly using conversational memory… respond ONLY with: FINISH` | Don't run tools for memory questions. |

## `answer.py`: + uses memories

```python
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
        temperature=0,  # FIX: consistent answers
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
```

| New | Meaning |
|-----|---------|
| `Relevant previous memories: {state["memories"]}` | This is how **"What is my name?"** gets answered. |
| `Use relevant previous memories when they help…` | Use memories when useful. |
| **FIX** `Only use a memory if it is clearly about this user's question.` | Recall is noisy (threshold 0.20), so don't let unrelated memories leak into answers. |

## `loop.py`: recall → plan → act → answer → save

```python
from state import (
    create_state,
    add_task,
    add_action,
    record_observation,
    add_result,
    complete_task,
    all_tasks_completed,
    next_step,
    can_continue,
    finish
)

from task_planner import (
    decompose_task
)

from state import add_memory

from memory import (
    save_memory,
    search_semantic_memories
)


def parse_decision(decision):

    task = None
    tool = None

    # Handle the normal two-line format
    for line in decision.splitlines():

        line = line.strip()

        if line.startswith("TASK:"):

            task = line[5:].strip()

        elif line.startswith("TOOL:"):

            tool = line[5:].strip()

    # Handle the case where the LLM puts
    # TASK and TOOL on the same line.
    if task and "TOOL:" in task:

        parts = task.split(
            "TOOL:",
            1
        )

        task = parts[0].strip()

        if not tool:

            tool = parts[1].strip()

    # FIX: clean the tool name (backticks, quotes, dots, spaces)
    if tool:
        tool = tool.strip().strip(" .`'\"").split()[0]

    return task, tool




async def run_agent_loop(
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):

    state = create_state(
        user_request,
        max_steps=8  # FIX: room for retries (was 5)
    )

    # --------------------------------
    # Step 0: Recall relevant memories
    # --------------------------------

    memories = search_semantic_memories(
        user_request,
        top_k=3
    )

    for memory in memories:

        add_memory(
            state,
            memory
        )

    print("\nRelevant Memories")
    print("-----------------")

    for memory in state["memories"]:

        print(
            f"- ({memory['score']:.2f})",
            memory["user_message"]
        )

    if not state["memories"]:
        print("- none")

    # --------------------------------
    # Step 1: Decompose the goal
    # --------------------------------

    planned_tasks = decompose_task(
        user_request
    )

    for task in planned_tasks:

        add_task(
            state,
            task
        )

    print("\nTask Plan")
    print("---------")

    for item in state["tasks"]:

        print(
            "-",
            item["task"]
        )

    # FIX: no tasks (greeting, introduction, memory question,
    # general question) -> answer directly, no loop needed
    if not state["tasks"]:

        print("- (no tasks - answering directly)")

        finish(
            state,
            format_answer(state)
        )

    # --------------------------------
    # Step 2: Autonomous loop
    # --------------------------------

    while can_continue(state):

        # --------------------------------
        # Check whether all tasks are done
        # --------------------------------

        if all_tasks_completed(state):

            print(
                "\n--- Step "
                f"{state['current_step'] + 1} ---"
            )

            print(
                "Planner Decision:"
            )

            print("TASK: FINISH")

            answer = format_answer(
                state
            )

            finish(
                state,
                answer
            )

            break

        print(
            f"\n--- Step "
            f"{state['current_step'] + 1} ---"
        )

        # --------------------------------
        # Ask planner for next task
        # --------------------------------

        decision = planner(
            state,
            tools
        )

        print(
            "Planner Decision:"
        )

        print(decision)

        # --------------------------------
        # Check FINISH
        # --------------------------------

        if decision.strip().upper() == "FINISH":

            answer = format_answer(
                state
            )

            finish(
                state,
                answer
            )

            break

        # --------------------------------
        # Extract task and tool
        # --------------------------------

        task, tool = parse_decision(
            decision
        )

        if not task or not tool:

            add_result(
                state,
                "Invalid planner decision."
            )

            next_step(state)

            continue

        state["current_task"] = task

        # --------------------------------
        # Execute tool
        # --------------------------------

        observation = await execute_action(
            tool,
            state,
            client
        )

        print(
            "Observation:",
            observation
        )

        # --------------------------------
        # Update state
        # --------------------------------

        add_action(
            state,
            tool
        )

        record_observation(
            state,
            tool,
            observation
        )

        add_result(
            state,
            observation
        )

        # --------------------------------
        # Mark task complete
        # --------------------------------

        if not observation.lower().startswith(
            "error"
        ):

            complete_task(
                state,
                task
            )

            print(
                "completed"
            )

        else:

            add_result(
                state,
                "The previous action failed. "
                "The planner must reconsider."
            )

        next_step(state)

    # FIX: max_steps reached without finishing ->
    # still give the user an answer from what was done
    if not state["finished"]:

        print("\nMax steps reached - answering with results so far.")

        finish(
            state,
            format_answer(state)
        )

    # --------------------------------
    # Step 3: Save to long-term memory
    # FIX: saved in ONE place, after every run
    # (the course saved only when the planner said FINISH)
    # --------------------------------

    save_memory(
        user_request,
        state["final_answer"]
    )

    return state
```

### What's new compared to Day 10

| # | Stage | Code |
|---|-------|------|
| ① | **Recall** | `search_semantic_memories(user_request, top_k=3)` → `add_memory()` for each → print `Relevant Memories` with scores |
| ② | Plan | `decompose_task()` (same as Day 10) |
| 🆕 | **No tasks → answer directly** | **FIX:** `if not state["tasks"]:` → `format_answer` → `finish` (the loop is skipped) |
| ③ | Act | The same Day 10 loop (planner → executor → tick tasks → safety net) |
| ⑤ | **Save** | **FIX:** `save_memory(user_request, state["final_answer"])` runs **once, after every run** |

> 💡 **Why save in one place?** The course version saved only inside the `if decision == "FINISH"` branch. But Day 10's loop usually finishes through the **code** check (`all_tasks_completed`), so for tool requests the conversation was **never saved**. One save at the end means **every run** is remembered.

## `runner.py`: + create_database

```python
import asyncio

from mcp_client import (
    connect,
    disconnect,
    discover_tools
)

from planner import planner
from executor import execute_action
from loop import run_agent_loop
from answer import format_answer
from memory import create_database

async def main():
    create_database()
    client = await connect()

    tools = await discover_tools(
        client
    )

    print("\nAvailable Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)

    user_request = input(
        "\nUser : "
    )

    state = await run_agent_loop(
        user_request,
        planner,
        execute_action,
        format_answer,
        tools,
        client
    )

    print("\nFinal Answer")
    print("------------")

    print(
        state["final_answer"]
    )

    await disconnect(client)


if __name__ == "__main__":
    asyncio.run(main())
```

The only change from Day 10 is `create_database()` at the start, which makes sure the `memories` table exists before anything is searched or saved.

## `executor.py`, `server.py`, `mcp_client.py`

Unchanged from the **fixed** Day 10 / Day 8 versions:

```python
from mcp_client import execute_tool


async def execute_action(
    action,
    state,
    client
):

    # FIX: some tasks need no tool (e.g. "Explain Python").
    # The answer generator will handle them from general knowledge.
    if action.lower() == "none":
        return "No tool needed. Answer this task from general knowledge."

    # FIX: a wrong tool name must not crash the agent
    try:

        result = await execute_tool(
            client,
            action
        )

    except Exception as error:

        return f"Error: {error}"

    if hasattr(result, "content"):

        if result.content:
            return result.content[0].text

    return str(result)
```

```python
from datetime import datetime

from fastmcp import FastMCP

mcp = FastMCP("Time Server")

@mcp.tool()

def current_time():

    """Return the current date and time."""

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


import random

@mcp.tool()

def roll_dice():

    """Roll a six-sided dice."""

    return random.randint(1,6)

import secrets
import string

@mcp.tool()

def generate_password(length: int = 12):

    """
    Generate a secure password.
    """

    alphabet = (
        string.ascii_letters
        + string.digits
        + string.punctuation
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )

import sys

if __name__ == "__main__":
    # FIX: stdout is the MCP channel - log to stderr only
    print("Starting MCP server..", file=sys.stderr)
    mcp.run()
```

```python
from fastmcp import Client

# FIX: in-memory connection (stdio fails on this PC - Day 8)
from server import mcp


async def connect():

    """
    Connect to the MCP Server.
    """

    client = Client(mcp)

    await client.__aenter__()

    print("Connected to MCP Server.")

    return client


async def disconnect(client):

    """
    Close the MCP connection.
    """

    await client.__aexit__(
        None,
        None,
        None
    )


async def discover_tools(client):

    """
    Retrieve all tools from the server.
    """

    tools = await client.list_tools()

    return tools


async def execute_tool(
    client,
    tool_name,
    arguments=None
):

    """
    Execute a tool.
    """

    if arguments is None:

        arguments = {}

    result = await client.call_tool(

        tool_name,

        arguments

    )

    return result
```

See the Day 8 and Day 10 READMEs for line-by-line explanations.

### 📤 Output — Part 2

#### Run 1 — `My name is Chandan and I am a QA engineer.`
```
 python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : My name is Chandan and I am a QA engineer

Relevant Memories
-----------------
- (0.93) My name is Chandan and I am a QA engineer.

Task Plan
---------
- (no tasks - answering directly)

Final Answer
------------
Hi Chandan, nice to meet you! As a QA engineer, you play a crucial role in ensuring software applicationsare functioning correctly. Your tasks involve testing and identifying bugs, which can be challenging at times. If you'd like to discuss any specific challenges you're facing or need help with your tasks, I'm here to assist you.
(venv) 
```

#### Run 2 (new run!) — `What is my name?`
```
python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : What is my name?

Relevant Memories
-----------------
- (0.45) My name is Chandan and I am a QA engineer.
- (0.42) My name is Chandan and I am a QA engineer

Task Plan
---------
- (no tasks - answering directly)

Final Answer
------------
Hello Chandan! You mentioned earlier that your name is Chandan and you are a QA engineer.
(venv) 
```

#### Run 3 — `What time is it?` (tool task + memory saved)
```
$ python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : What is my name?

Relevant Memories
-----------------
- (0.45) My name is Chandan and I am a QA engineer.
- (0.42) My name is Chandan and I am a QA engineer

Task Plan
---------
- (no tasks - answering directly)

Final Answer
------------
Hello Chandan! You mentioned earlier that your name is Chandan and you are a QA engineer.
(venv) 
chand@DESKTOP-4N0QCDO MINGW64 /d/AI Agents/AI_Agent_Journy/Day_11_Memory-Engineering/Day11_P2 (main)
$ python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : What time is it?

Relevant Memories
-----------------
- (0.46) What is my name?
- (0.43) My name is Chandan and I am a QA engineer.
- (0.41) My name is Chandan and I am a QA engineer

Task Plan
---------
- Get current system time
- Convert time to 12-hour format
- Display time to user

--- Step 1 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be completed with a different tool.
4. The task is not a completed action, and no other tool is available to complete it.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 2 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly from the pending task list.
2. The tool "current_time" is available and suitable for this task.
3. There are no other pending tasks that require different tools.
4. The task is not a completed action, and no other tool fits this task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 3 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be completed with a different tool.
4. The task is not a completed action, and no other tool is available to complete it.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 4 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be completed with a different tool.
4. The task is not a completed action, and no other tool is available to complete it.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 5 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be completed with a different tool.
4. The task is not a completed task, and the tool is suitable for the task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 6 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be completed with a different tool.
4. The task is not a completed action, and no other tool is available to fulfill this task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 7 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be completed with a different tool.
4. The task is not a completed action, and no other tool is available to complete it.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 8 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be selected.
4. The task is not a completed action, and no tool was previously selected for this task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

Max steps reached - answering with results so far.

Final Answer
------------
I don't have any relevant previous memories about the current time. However, I can tell you that as a QA engineer, you play a crucial role in ensuring software applications are functioning correctly. If you'd like to discuss any specific challenges you're facing or need help with your tasks, I'm here to assist you.
(venv)
```

**Observation:**
<!-- e.g. Run 2 recalled run 1's memory with the highest score and answered correctly — after restarting the program. -->

---

# Part 3 — The Memory Extractor 🧠

**Problem with P2:** it saves **every** conversation: *"What time is it?"*, *"Roll a dice"*, *"hi"*. Over time the memory fills with **noise**, recall gets worse, and the database grows for no reason.

**Solution:** before saving a fact, ask the LLM **"Is there anything here worth remembering long-term?"**

```
"What time is it?" / "The time is 10 PM."            → NONE           (not saved as a fact)
"I'm learning AI agents with Python." / "Great!..."  → "The user is learning AI agents with Python."   ✅ saved
```

## `memory_extractor.py`

```python
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
    prompt = f"""
You are a memory extraction system.

Read the conversation below and determine whether
it contains useful long-term information about the user.

User:
{user_message}

Assistant:
{assistant_message}

Store information only if it will be useful
in future conversations.

Useful information includes:
- preferences
- interests
- goals
- skills
- projects
- important user facts

Do NOT store:
- temporary questions
- current time
- random calculations
- one-time requests
- tool results
- casual conversation

If useful information exists,
return ONLY the fact that should be remembered.

If there is nothing useful to remember,
return:

NONE
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,  # FIX: consistent extraction
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
    if not fact or fact.upper().strip(" .") == "NONE":
        return "NONE"

    return fact
```

### Step-by-step explanation

| Prompt part | Purpose |
|-------------|---------|
| `You are a memory extraction system.` | Role. |
| `User: … Assistant: …` | The conversation to judge. |
| `Useful information includes: preferences, interests, goals, skills, projects, important user facts` | What to **keep**. |
| `Do NOT store: temporary questions, current time, random calculations, one-time requests, tool results, casual conversation` | What to **drop**. |
| `return ONLY the fact` / `return: NONE` | A machine-readable result. |

| FIX code | Why |
|----------|-----|
| `temperature=0` | Consistent decisions. |
| `if "</think>" in fact:` | Remove qwen3's thinking text. |
| `.strip().strip('"')` | Remove quotes around the fact. |
| `if not fact or fact.upper().strip(" .") == "NONE": return "NONE"` | The course compared `fact != "NONE"` **exactly**, so `NONE.`, `None` or an empty reply **were saved as memories**. |

## `test_memory_extractor.py`

```python
from memory_extractor import extract_memory


memory = extract_memory(
    "What is the current time?",
    "The current time is 10 PM."

)

print("Extracted Memory:")
print(memory)
```

A "current time" chat is a **temporary** question, so the expected output is `NONE`.

**Try more:**

```python
print(extract_memory("I prefer short answers.", "Okay!"))                  # → a preference fact
print(extract_memory("Roll a dice", "You rolled 4."))                      # → NONE
print(extract_memory("I'm building a QA automation tool in Python.", "Nice!"))  # → a project fact
```

## `memory.py` (P3): + `save_semantic_memory()`

```python
import json
import sqlite3

import numpy as np
from openai import OpenAI


DATABASE = "memory.db"


embedding_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            assistant_message TEXT,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def create_embedding(text):
    response = embedding_client.embeddings.create(
        model="nomic-embed-text",
        input=text
    )
    
    return response.data[0].embedding


def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    return np.dot(v1, v2) / (
        np.linalg.norm(v1) *
        np.linalg.norm(v2)
    )


def save_memory(user_message, assistant_message):
    text = user_message + "\n" + assistant_message

    embedding = create_embedding(text)
    

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (
            user_message,
            assistant_message,
            embedding
        )
        VALUES (?, ?, ?)
        """,
        (
            user_message,
            assistant_message,
            json.dumps(embedding)
        )
    )

    connection.commit()
    connection.close()


def search_semantic_memories(
    query,
    top_k=3,
    threshold=0.20
):
    query_embedding = create_embedding(query)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_message,
            assistant_message,
            embedding,
            created_at
        FROM memories
    """)

    rows = cursor.fetchall()

    connection.close()

    results = []

    for (
        user_message,
        assistant_message,
        embedding_json,
        created_at
    ) in rows:

        memory_embedding = json.loads(
            embedding_json
        )

        score = cosine_similarity(
            query_embedding,
            memory_embedding
        )
        
        if score >= threshold:
            results.append({
                "user_message": user_message,
                "assistant_message": assistant_message,
                "created_at": created_at,
                "score": score
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    #print(results)

    return results[:top_k]

def save_semantic_memory(fact):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    embedding = create_embedding(fact)

    cursor.execute(
        """
        INSERT INTO memories
        (
            user_message,
            assistant_message,
            embedding
        )
        VALUES (?, ?, ?)
        """,
        (
            fact,
            "",
            json.dumps(embedding)
        )
    )

    connection.commit()
    connection.close()
```

| New function | Meaning |
|--------------|---------|
| `save_semantic_memory(fact)` | Embed **only the fact** and save it as a row, with `user_message = fact` and `assistant_message = ""`. |

Because facts go in the **same table**, `search_semantic_memories()` finds **both** conversations and facts without any change. A fact like *"The user's name is Chandan."* is short and clear, so it usually scores **higher** than a full conversation.

## `loop.py` (P3): + extract & save facts

```python
from state import (
    create_state,
    add_task,
    add_action,
    record_observation,
    add_result,
    complete_task,
    all_tasks_completed,
    next_step,
    can_continue,
    finish
)

from task_planner import (
    decompose_task
)

from state import add_memory

from memory import (
    save_memory,
    search_semantic_memories,
    save_semantic_memory
)

from memory_extractor import extract_memory


def parse_decision(decision):

    task = None
    tool = None

    # Handle the normal two-line format
    for line in decision.splitlines():

        line = line.strip()

        if line.startswith("TASK:"):

            task = line[5:].strip()

        elif line.startswith("TOOL:"):

            tool = line[5:].strip()

    # Handle the case where the LLM puts
    # TASK and TOOL on the same line.
    if task and "TOOL:" in task:

        parts = task.split(
            "TOOL:",
            1
        )

        task = parts[0].strip()

        if not tool:

            tool = parts[1].strip()

    # FIX: clean the tool name (backticks, quotes, dots, spaces)
    if tool:
        tool = tool.strip().strip(" .`'\"").split()[0]

    return task, tool




async def run_agent_loop(
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):

    state = create_state(
        user_request,
        max_steps=8  # FIX: room for retries (was 5)
    )

    # --------------------------------
    # Step 0: Recall relevant memories
    # --------------------------------

    memories = search_semantic_memories(
        user_request,
        top_k=3
    )

    for memory in memories:

        add_memory(
            state,
            memory
        )

    print("\nRelevant Memories")
    print("-----------------")

    for memory in state["memories"]:

        print(
            f"- ({memory['score']:.2f})",
            memory["user_message"]
        )

    if not state["memories"]:
        print("- none")

    # --------------------------------
    # Step 1: Decompose the goal
    # --------------------------------

    planned_tasks = decompose_task(
        user_request
    )

    for task in planned_tasks:

        add_task(
            state,
            task
        )

    print("\nTask Plan")
    print("---------")

    for item in state["tasks"]:

        print(
            "-",
            item["task"]
        )

    # FIX: no tasks (greeting, introduction, memory question,
    # general question) -> answer directly, no loop needed
    if not state["tasks"]:

        print("- (no tasks - answering directly)")

        finish(
            state,
            format_answer(state)
        )

    # --------------------------------
    # Step 2: Autonomous loop
    # --------------------------------

    while can_continue(state):

        # --------------------------------
        # Check whether all tasks are done
        # --------------------------------

        if all_tasks_completed(state):

            print(
                "\n--- Step "
                f"{state['current_step'] + 1} ---"
            )

            print(
                "Planner Decision:"
            )

            print("TASK: FINISH")

            answer = format_answer(
                state
            )

            finish(
                state,
                answer
            )

            break

        print(
            f"\n--- Step "
            f"{state['current_step'] + 1} ---"
        )

        # --------------------------------
        # Ask planner for next task
        # --------------------------------

        decision = planner(
            state,
            tools
        )

        print(
            "Planner Decision:"
        )

        print(decision)

        # --------------------------------
        # Check FINISH
        # --------------------------------

        if decision.strip().upper() == "FINISH":

            answer = format_answer(
                state
            )

            finish(
                state,
                answer
            )

            break

        # --------------------------------
        # Extract task and tool
        # --------------------------------

        task, tool = parse_decision(
            decision
        )

        if not task or not tool:

            add_result(
                state,
                "Invalid planner decision."
            )

            next_step(state)

            continue

        state["current_task"] = task

        # --------------------------------
        # Execute tool
        # --------------------------------

        observation = await execute_action(
            tool,
            state,
            client
        )

        print(
            "Observation:",
            observation
        )

        # --------------------------------
        # Update state
        # --------------------------------

        add_action(
            state,
            tool
        )

        record_observation(
            state,
            tool,
            observation
        )

        add_result(
            state,
            observation
        )

        # --------------------------------
        # Mark task complete
        # --------------------------------

        if not observation.lower().startswith(
            "error"
        ):

            complete_task(
                state,
                task
            )

            print(
                "completed"
            )

        else:

            add_result(
                state,
                "The previous action failed. "
                "The planner must reconsider."
            )

        next_step(state)

    # FIX: max_steps reached without finishing ->
    # still give the user an answer from what was done
    if not state["finished"]:

        print("\nMax steps reached - answering with results so far.")

        finish(
            state,
            format_answer(state)
        )

    # --------------------------------
    # Step 3: Save to long-term memory
    # FIX: saved in ONE place, after every run
    # (the course saved only when the planner said FINISH)
    # --------------------------------

    save_memory(
        user_request,
        state["final_answer"]
    )

    fact = extract_memory(
        user_request,
        state["final_answer"]
    )

    print("\nMemory Extracted:", fact)

    if fact != "NONE":

        save_semantic_memory(fact)

    return state
```

Compared to P2, the save step now does **two** things:

```python
save_memory(user_request, state["final_answer"])        # episodic: the whole conversation

fact = extract_memory(user_request, state["final_answer"])
print("\nMemory Extracted:", fact)

if fact != "NONE":
    save_semantic_memory(fact)                          # semantic: only the useful fact
```

All other P3 files (`state.py`, `task_planner.py`, `planner.py`, `answer.py`, `runner.py`, `executor.py`, `server.py`, `mcp_client.py`, `test_memory.py`) are **identical to P2**.

### 📤 Output — Part 3

#### `python test_memory_extractor.py`
```
$ python test_memory_extractor.py
Extracted Memory:
NONE
(venv) 
```

#### Run 1 — `I am learning AI agents with Python.`
```
 python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : I am learning AI agents with Python.

Relevant Memories
-----------------
- none

Task Plan
---------
- Learn basics of Python programming
- Create a new Python project
- Install necessary libraries for AI
- Search for AI agent tutorials on Python
- Watch introductory AI agent videos on YouTube
- Read AI agent documentation on Python
- Create a simple AI agent using Python
- Test and debug the AI agent
- Implement reinforcement learning in Python
- Experiment with different AI agent algorithms
- Document the AI agent project
- Share the AI agent project on GitHub

--- Step 1 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Search for AI agent tutorials on Python'
TOOL: current_time

Reasoning: Since the task is to search for AI agent tutorials on Python, I will use the current_time toolto provide the current date and time, which can be used to search for relevant tutorials online.

--- Step 2 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Search for AI agent tutorials on Python'
TOOL: current_time

Reasoning: Since the task is 'Search for AI agent tutorials on Python', I will use the 'current_time' tool to provide a timestamp for when the task was completed. This will help track progress and ensure that the task is completed in a timely manner.

Please note that this is a simple task that can be completed using a search engine or online resources, and the 'current_time' tool is not directly related to the task itself. However, it is the best available tool to provide a timestamp for when the task is completed.

--- Step 3 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Search for AI agent tutorials on Python'
TOOL: current_time

Reasoning: Since the task is to search for AI agent tutorials on Python, I will use the current_time toolto provide the current date and time, which can be used to search for relevant tutorials online.

--- Step 4 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Search for AI agent tutorials on Python
TOOL: generate_password

However, I realize that generating a password is not the best tool for searching for tutorials. I will reconsider the task.

TASK: Search for AI agent tutorials on Python
TOOL: roll_dice

No, rolling a dice is not relevant to searching for tutorials.

TASK: Search for AI agent tutorials on Python
TOOL: current_time

No, the current time is not relevant to searching for tutorials.

Since none of the tools seem suitable for searching for tutorials, I will use the "none" tool.

TASK: Search for AI agent tutorials on Python
TOOL: none
Observation: No tool needed. Answer this task from general knowledge.
completed

--- Step 5 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Watch introductory AI agent videos on YouTube
TOOL: roll_dice

However, this is not a suitable tool for watching videos. I will reconsider the task.

After re-evaluating the tasks, I recommend the following:

TASK: Watch introductory AI agent videos on YouTube
TOOL: current_time

This is still not a suitable tool for watching videos. I will reconsider the task again.

After re-evaluating the tasks again, I recommend the following:

TASK: Watch introductory AI agent videos on YouTube
TOOL: none

This task cannot be completed with the available tools.
Observation: No tool needed. Answer this task from general knowledge.
completed

--- Step 6 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Read AI agent documentation on Python'
TOOL: 'read_documentation'

Reasoning:

1. The task 'Read AI agent documentation on Python' is still pending and has not been completed.
2. The task is related to learning AI agents with Python, which is the user's current goal.
3. The tool 'read_documentation' is not explicitly listed in the available tools, but it can be inferred that it would involve reading documentation, which is a common task in learning AI agents.
4. Since there are no observations or results related to this task, I will assume that the user needs to start from scratch and read the documentation.

However, I noticed that the task 'Read AI agent documentation on Python' is not in the exact format required by the rules. I will modify it to fit the format:

TASK: Read AI agent documentation on Python
TOOL: read_documentation
Tool 'read_documentation' not listed, no validation will be performed
Observation: Error: Unknown tool: read_documentation

--- Step 7 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Read AI agent documentation on Python'
TOOL: 'read_documentation'

However, since 'read_documentation' is not a valid tool, I will reconsider the task.

Task: 'Read AI agent documentation on Python'
TOOL: 'none'

Since there is no tool available to complete this task, I will return the result as specified in rule 7b.

FINISH

--- Step 8 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Read AI agent documentation on Python'
TOOL: 'read_documentation'

However, since 'read_documentation' is not a valid tool, I will reconsider the task.

Task: 'Read AI agent documentation on Python'
TOOL: 'none'

Since there is no valid tool available for this task, I will return the result as specified in rule 7b.

FINISH

Max steps reached - answering with results so far.

Memory Extracted: NONE

Final Answer
------------
It seems like you've already completed some tasks related to AI and Python, such as watching introductoryAI agent videos on YouTube and reading AI agent documentation on Python. You've also started working on creating a simple AI agent using Python, but you haven't finished testing and debugging it yet.

For your current task, "Create a simple AI agent using Python," you've encountered an error when trying to read the documentation. This is because the "read_documentation" action is not a valid action for this task.

To move forward, you could try to implement reinforcement learning in Python, which is a key concept in AI agents. You can start by researching how to implement reinforcement learning in Python and see if you can find any resources or tutorials that can help you with this task.

Additionally, you may want to consider experimenting with different AI agent algorithms to see which one works best for your project. You can also document your project and share it on GitHub once you've completed the testing and debugging phase.

Let me know if you need any further guidance or if there's anything else I can help you with!
(venv)
```

#### Run 2 — `What time is it?` (expect `Memory Extracted: NONE`)
```
$ python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : What time is it?

Relevant Memories
-----------------
- (0.30) I am learning AI agents with Python.

Task Plan
---------
- Get current system time
- Convert time to 12-hour format
- Display time to user

--- Step 1 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

* The task "Get current system time" is exactly copied from the pending task list.
* The tool "current_time" is available and matches the task requirement.
* There are no other pending tasks that can be completed with a different tool.
* The task is a simple and straightforward request that can be answered directly using conversational memory.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 2 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:
The task "Get current system time" is a simple task that requires retrieving the current date and time. The tool "current_time" is specifically designed to return the current date and time, making it the most suitable tool for this task.

--- Step 3 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and can be used to complete the task.
3. There are no other pending tasks that can be completed with the available tools.
4. The task is not a completed task, and the tool is suitable for the task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 4 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and can be used to complete the task.
3. There are no other pending tasks that can be completed with the available tools.
4. The task is not a completed task, and the tool is suitable for the task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 5 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and can be used to complete the task.
3. There are no other pending tasks that can be completed with the available tools.
4. The task is not a completed task, and the tool is suitable for the task.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

--- Step 6 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:
The task "Get current system time" is a simple and straightforward request that can be answered directly using conversational memory. The tool "current_time" is available and can be used to provide the current system time. This decision is based on the fact that the task is already in the pending list and can be answered directly using the available tool.

--- Step 7 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:
The task "Get current system time" is a simple and straightforward request that can be answered directly using conversational memory. The tool "current_time" is available and can be used to provide the current system time. This decision is based on the fact that the task is already in the pending list and can be answered directly using the available tool.

--- Step 8 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: Get current system time
TOOL: current_time

Reasoning:

1. The task "Get current system time" is exactly copied from the pending task list.
2. The tool "current_time" is available and matches the task requirement.
3. There are no other pending tasks that can be selected.
4. The task is not a completed task, and the tool is available.

Therefore, the next decision is to select the task "Get current system time" and the tool "current_time".

Max steps reached - answering with results so far.

Memory Extracted: Based on the conversation, I will store the following information:

NONE

The conversation is a simple query about the current time, which is not a useful long-term fact.

Final Answer
------------
I'm not currently able to provide the system time.
(venv)
```

#### Run 3 — `What am I learning?`
```
runtime too much so i did not add output
```

**Observation:**

---

# Part 4 — Final Integration: Test Semantic Memory 🧪

P4's code is **identical to P3**. Use it for the full end-to-end test from lessons 142–143.

**Suggested test script** (each line is a **new run** of `python runner.py`):

| Run | You type | Expect |
|-----|----------|--------|
| 1 | `My name is Chandan and I am a QA engineer.` | `Memory Extracted:` a name/role fact |
| 2 | `I want to become an AI engineer.` | A goal fact |
| 3 | `Roll a dice and tell me the time.` | Tools run, `Memory Extracted: NONE` |
| 4 | `What is my name and what is my goal?` | Recalled facts → correct answer |
| 5 | `Generate a password and tell me what I do for work.` | A tool + memory in one answer |

### 📤 Output — Part 4

#### Runs 1–5
```
python runner.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : My name is Chandan and I am a QA engineer

Relevant Memories
-----------------
- none

Task Plan
---------
- (no tasks - answering directly)

Memory Extracted: User:
My name is Chandan and I am a QA engineer

Assistant:
Chandan, your role as a QA engineer involves testing software applications to ensure they are functioningcorrectly and identifying bugs.

Final Answer
------------
Hello Chandan! It's nice to meet you. I don't have any relevant previous memories about you. As a QA engineer, I can tell you that your role involves testing software applications to ensure they are functioning correctly and identifying bugs. If you'd like to discuss your tasks or any specific challenges you're facing, I'm here to help.
(venv)

runtime too much so i did not add output
```

**Observation:**

---

## 🔍 Day 10 → Day 11 P2 → P3/P4

| | Day 10 | Day 11 P2 | Day 11 P3/P4 |
|---|---|---|---|
| Remembers after restart | ❌ | ✅ | ✅ |
| Storage | — | SQLite (`memory.db`) | SQLite |
| What's saved | — | Every conversation (episodic) | Conversations + **extracted facts** (semantic) |
| How it's recalled | — | Embeddings + cosine similarity, top 3 | Same |
| Memory used by | — | Planner + answer | Planner + answer |
| Greetings / memory questions | Run through the planner | **No tasks**, answered directly | Same |
| Extra LLM calls per run | — | +1 embedding (search) +1 (save) | + extraction call + fact embedding |

---

## ⚠️ Remaining Limitations / Next Improvements

1. **Duplicate facts.** The same fact is saved every time it comes up. Fix: before saving, search for the fact; if a memory scores above ~0.9, skip it (or update it).
2. **No updating or forgetting.** "I live in Delhi" → "I moved to Mumbai" keeps **both**. Real systems update, merge or expire memories, and let the user delete them.
3. **Noisy recall (threshold 0.20).** Unrelated memories get into the prompt. Tune the threshold based on real scores (e.g. 0.5), and/or recall facts before conversations.
4. **Search loads every row.** It's fine for learning, but slow with thousands of memories. Use a vector database (Chroma, FAISS, Qdrant) or `sqlite-vec`.
5. **One memory for everyone.** There's no `user_id` column, so two users of the same agent would share memories. Add a `user_id` to the table and to every query.
6. **Privacy.** There's no way to view or delete memories from the app, and no filter that stops sensitive data (passwords, IDs) being saved. Add a "forget" command and an extractor rule against sensitive data.
7. **Memory is passed as raw dicts.** The prompt gets Python dicts, including scores and timestamps. Formatting them as simple lines (`- The user's name is Chandan.`) helps small models.
8. **Relative DB path.** `memory.db` is created wherever you run from, so running from another folder gives an **empty** memory. Use a path based on `__file__` for a fixed location.
9. **The embedding client is hard-coded** (`localhost:11434`, `nomic-embed-text`). Move it to `.env` like the chat model.
10. **Separate LLM clients in 4 files.** One shared `llm.py` would be cleaner.

---

## 🛠️ Troubleshooting

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| The agent calls you **Pankaj** 😄 | The course `memory.db` holds the author's test memories | `rm memory.db` in each part folder |
| `Connection refused` / error in `create_embedding` | Ollama isn't running, or `nomic-embed-text` is missing | `ollama serve`, `ollama pull nomic-embed-text` |
| `ModuleNotFoundError: No module named 'numpy'` | Not installed in the venv | `python -m pip install numpy` |
| `sqlite3.OperationalError: no such table: memories` | `create_database()` wasn't called | Run via `runner.py` (it calls it), or call `create_database()` first |
| Run 2 doesn't remember run 1 | Different folder → different `memory.db` | Run both from the same part folder |
| Task Plan shows a task called `NONE` | Course `task_planner.py` | Use the fixed version above |
| Tool requests are never remembered | Course `loop.py` saved only on `FINISH` | Use the fixed `loop.py` (saves after every run) |
| `Memory Extracted: NONE.` appears in the DB as a memory | Course extractor compared the text exactly | Use the fixed `memory_extractor.py` |
| `ToolError: Unknown tool` | Course executor | The fixed `executor.py` (Day 10) |
| `MCPError: Connection closed` | stdio on this PC | In-memory `mcp_client.py` (Day 8) |
| Traceback shows `...\Python310\...` | The venv isn't really active | `source venv/Scripts/activate` → check `which python` |

---

## ✅ Key Takeaways

- An LLM remembers nothing by itself. **Memory is engineered around it.**
- **Memory engineering** = deciding **what** to store, **where**, **how to find it** and **what to forget**.
- **Short-term** memory = the agent state (one run). **Long-term** memory = a database (survives restarts).
- **Episodic** memory stores conversations; **semantic** memory stores **extracted facts**, which are smaller and cleaner.
- Memory search is **RAG over your own past**: embeddings + cosine similarity + top-k.
- A **memory extractor** keeps the important and drops the noise ("current time" → `NONE`).
- Memory brings **personalisation**, but also **privacy, accuracy and staleness** responsibilities.

---

