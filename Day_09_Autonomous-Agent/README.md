# Day 09 — Building an Autonomous AI Agent 🤖🔁

Part of the **AI_Agent_Journy** day-by-day learning series.

| Day | Topic |
|-----|-------|
| Day 01 | Ollama chatbot |
| Day 02 | AI assistant with memory |
| Day 03 | Prompt engineering — system prompts & roles |
| Day 04 | AI tools — keyword-based tool selection |
| Day 05 | Document AI — read, summarize, explain and question files |
| Day 06 | RAG — find the right document by meaning |
| Day 07 | AI planner — the model chooses the tool |
| Day 08 | MCP — tools in a server, discovered at runtime |
| **Day 09** | **Autonomous agent — the AI keeps planning and acting, step by step, until the goal is done** |

---

## 🎯 Goal of Day 9

Until Day 8, the agent did **one thing per request**:

```
"Roll a dice"  →  plan ONE tool  →  run it  →  answer  →  done
```

But real requests often need **several steps**:

```
"Generate a password AND tell me the current time"
```

The Day 8 agent can only pick one tool, so half the request is lost.

On Day 9 the agent becomes **autonomous**. It works in a **loop**:

```
plan the next step → do it → remember the result → plan again … → "I'm done" → answer
```

…and it decides **by itself** how many steps are needed and when to stop.

---

## 🤔 What Is an Autonomous AI Agent?

An **autonomous AI agent** is a program that is given a **goal**, then **repeatedly decides and performs actions on its own** until the goal is reached, without a human choosing each step.

> 🧑‍🍳 **Analogy: a chef with a recipe goal.**
> You say: *"Make breakfast: eggs and tea."*
> A **non-autonomous** helper does one thing and then waits for you to say the next one.
> An **autonomous** chef thinks *"What's next? Eggs aren't done… boil water… tea's not done… make tea… Both done? Yes → serve."* It **keeps going by itself** and **knows when to stop**.

### Assistant vs agent vs autonomous agent

| | Chatbot (Days 1–3) | Tool-using agent (Days 4–8) | **Autonomous agent (Day 9)** |
|---|---|---|---|
| Uses tools | ❌ | ✅ | ✅ |
| Steps per request | 1 answer | **1 tool** | **Many tools, as needed** |
| Who decides the next step | — | The AI, once | The AI, **again after every step** |
| Remembers what it already did | Chat history | ❌ | ✅ **Agent state** |
| Knows when it's finished | — | Always after 1 step | ✅ Returns `FINISH` |

---

## ⚙️ How It Works: The Agent Loop

The heart of every autonomous agent is a loop: **Think → Act → Observe → repeat**. (In research this is often called the **ReAct** pattern: *Reason + Act*.)

```
                ┌─────────────────────────────┐
  User goal ──► │        AGENT STATE           │ ◄─── remembers everything
                │ request, step, actions,      │
                │ observations, finished       │
                └──────────────┬──────────────┘
                               │
              ┌────────────────▼────────────────┐
              │ 1. THINK   planner (LLM)         │  "What should I do NEXT?"
              │    reads state + tool list       │
              └────────────────┬────────────────┘
                     tool name │        "FINISH"
              ┌────────────────▼───┐        │
              │ 2. ACT  executor    │        │
              │  runs tool via MCP  │        │
              └────────────────┬───┘        │
              ┌────────────────▼───┐        │
              │ 3. OBSERVE          │        │
              │ save result → state │        │
              └────────────────┬───┘        │
                               │            │
                   step < max_steps?        │
                     yes → back to 1        │
                               │            ▼
                               └──► 4. ANSWER  format_answer (LLM)
                                     turns all observations into
                                     one natural reply
```

### Example: one real run

**Request:** *"Generate a password and tell me the current time."*

| Step | Planner sees (state) | Planner decides | Executor result (observation) |
|------|----------------------|-----------------|-------------------------------|
| 0 | actions: `[]` | `generate_password` | `X#8Lm@4P...` |
| 1 | actions: `[generate_password]` | `current_time` | `02-11-2026 21:30:05` |
| 2 | actions: `[generate_password, current_time]` | `FINISH` | — |
| ✅ | | `format_answer()` | *"Here's your password: X#8Lm@4P… and the time is 21:30."* |

The planner was called **3 times**. Each time it looked at **what's already done** and chose **only the next step**.

### The building blocks

| Component | Job | File |
|-----------|-----|------|
| 🎯 **Goal** | What the user wants | `user_request` |
| 🧠 **State** | The agent's working memory: steps, actions, observations, finished | `state.py` |
| 🧭 **Planner** | The **brain**: picks the next action or `FINISH` | `planner.py` |
| 🛠️ **Executor** | The **hands**: runs the chosen action through MCP | `executor.py` |
| 🔌 **Tools** | The actual capabilities (time, dice, password) | `server.py` (MCP server) |
| 🔁 **Loop** | Repeats think → act → observe, and enforces stop rules | `loop.py` |
| 🛑 **Stop conditions** | `FINISH` from the planner, **or** the `max_steps` safety limit | `can_continue()` |
| 💬 **Answer formatter** | Writes one final, human-friendly reply | `format_answer()` in `runner.py` |
| ▶️ **Runner** | Wires everything together and starts the agent | `runner.py` |

---

## ✅ Why Autonomous Agents? (Benefits)

| Benefit | Explanation |
|---------|-------------|
| 🔗 **Multi-step tasks** | One request can trigger as many tool calls as needed. |
| 🧠 **Adapts as it goes** | Each step uses the **results of previous steps** to decide the next one. |
| 🙌 **Less human effort** | You give the goal, not every instruction. |
| 🧩 **Reuses everything before** | Planner (Day 7) + MCP tools (Day 8) + grounding (Days 5–6), now in a loop. |
| 📈 **Scales with tools** | Add a tool to the MCP server and the agent can use it in any step. No loop change. |
| 🔍 **Traceable** | The state records every action and observation, so you can see exactly *why* it answered what it did. |

## ⚠️ Limitations of Autonomous Agents

| Limitation | Explanation |
|------------|-------------|
| 🔁 **Can loop or repeat** | The LLM may pick the same action again or never say `FINISH`. That's why `max_steps` exists. |
| 🐢💸 **Slow and costly** | N steps = N + 1 planner calls + 1 answer call. With paid APIs, every step costs money. |
| 🤥 **Wrong decisions** | The planner can pick a wrong tool, invent a tool name, or finish too early. |
| ⛓️ **Errors compound** | A bad step 1 makes steps 2, 3… worse, because each step builds on the last. |
| 🎲 **Not deterministic** | The same request can take different paths on different runs, which makes it **hard to test**. |
| 📏 **State grows** | Long tasks mean long prompts, which risks hitting the context window. |
| 🔐 **Safety risk** | With real tools (delete files, send emails, payments), an autonomous mistake has real consequences. It needs **guardrails** and a **human in the loop**. |
| 🧨 **Prompt injection** | Tool results (web pages, emails) can contain text that tricks the planner into harmful actions. |

> **Rule of thumb:** give agents **autonomy over safe, reversible actions**, and require **human approval** for risky or irreversible ones.

## 🌍 Real-Life Applications

| Area | What an autonomous agent does |
|------|------------------------------|
| 💻 **Coding agents** | Read code → edit files → run tests → fix failures → repeat until the tests pass (e.g. Claude Code, GitHub Copilot agent mode, Cursor) |
| 🧪 **QA / test automation** | Read a requirement → generate test cases → run them → analyse failures → file bug reports |
| 🎧 **Customer support** | Look up the order → check the refund policy → issue the refund → write the reply |
| 🔬 **Research** | Search → read sources → take notes → search again for gaps → write a summary |
| 🛠️ **DevOps / incidents** | Read the alert → check logs → check metrics → suggest or apply a fix → report |
| 📊 **Data analysis** | Load the data → clean it → compute stats → plot → explain the findings |
| ✈️ **Personal assistants** | Check the calendar → find flights → compare prices → draft an itinerary for approval |

---

## 🧩 The 2 Parts at a Glance

| Part | Course lessons | What we build | Files |
|------|----------------|---------------|-------|
| **P1** | 111–116 | The **agent state**: the agent's working memory, tested alone | `state.py`, `test_state.py` |
| **P2** | 117–122 | The **complete autonomous agent**: loop + planner + MCP executor + runner | `loop.py`, `planner.py`, `executor.py`, `runner.py`, `server.py`, `mcp_client.py` |

---

## 📁 Folder Structure

```
Day_09_Autonomous-Agent/
├── README.md
├── Day09_P1/
│   └── agent/
│       ├── state.py          # agent state (memory)
│       └── test_state.py     # test the state alone
└── Day09_P2/
    └── agent/
        ├── state.py          # same as P1
        ├── test_state.py     # same test (import fixed)
        ├── server.py         # MCP server: 3 tools (from Day 8)
        ├── mcp_client.py     # MCP client helpers (from Day 8, in-memory)
        ├── planner.py        # chooses the NEXT action or FINISH
        ├── executor.py       # runs an action via MCP
        ├── loop.py           # the agent loop
        └── runner.py         # ▶️ START HERE: wires everything together
```

### How the files connect

```
runner.py
 ├── mcp_client.py ──► server.py        (connect, discover tools)
 ├── loop.py
 │    ├── state.py                      (create / update state)
 │    ├── planner.py   (passed in)      (LLM: next action?)
 │    └── executor.py  (passed in)      (run action)
 │          └── mcp_client.py ──► server.py
 └── format_answer()                    (LLM: final reply)
```

---

## 🔧 Changes from the Course Files (Day 8 lessons applied)

Two files in the course zip have problems we already solved on Day 8, and one has a broken import. **The code in this README is the working version.**

| File | Course version | This README | Why |
|------|----------------|-------------|-----|
| `server.py` | `print("Starting MCP server..")` | `print(..., file=sys.stderr)` | With stdio, stdout is the MCP channel, and a plain print breaks it (Day 8 Troubleshooting #2) |
| `mcp_client.py` | `Client("server.py")` (stdio) | `from server import mcp` → `Client(mcp)` (in-memory) | On this Windows + Git Bash PC, stdio fails with `Connection closed` (Day 8 Troubleshooting #5) |
| `test_state.py` (P2) | `from Day09.agent.state import *` | `from state import *` | There is no `Day09` package, so the original raises `ModuleNotFoundError` |

---

## ⚙️ Setup

Nothing new to install. Same as Day 8: shared venv, root `.env`, and `fastmcp<3`.

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
which python                  # must show .../AI_Agent_Journy/venv/Scripts/python
```

> **Model tip:** the zip's `.env` uses `qwen3:4b`. Thinking models may answer with `<think>...</think>` text instead of only a tool name or `FINISH`, so the loop can't recognise the action (see limitation #1). **`llama3.2` is recommended** in the root `.env`:
> ```env
> MODEL=llama3.2
> ```

Delete the per-part `.env` files, so the root `.env` is used (Day 5 lesson):

```bash
cd "/d/AI Agents/AI_Agent_Journy"
rm -f Day_09_Autonomous-Agent/Day09_P*/.env
```

---

## ▶️ How to Run: Which File First?

> ⚠️ Note the extra **`agent/`** folder. Run each script from **inside `agent/`**, because imports like `from state import ...` look in the current folder.
>
> 🔑 You **don't** run `server.py` yourself; `mcp_client.py` imports it.

| # | Folder | Command | What it does | Expected |
|---|--------|---------|--------------|----------|
| 1 | `Day09_P1/agent` | `python test_state.py` | Tests the state alone: no AI, no MCP | 3 printed state dictionaries |
| 2 | `Day09_P2/agent` | `python test_state.py` | Same test in P2 (optional) | Same as #1 |
| 3 | `Day09_P2/agent` | `python runner.py` | ▶️ **The autonomous agent** | Tool list → `Planner Selected:` lines → `Final Answer:` |

```bash
cd "/d/AI Agents/AI_Agent_Journy/Day_09_Autonomous-Agent/Day09_P1/agent"
python test_state.py

cd ../../Day09_P2/agent
python runner.py
```

**Good requests to try in `runner.py`:**

| Request | Expected steps |
|---------|----------------|
| `Generate a password and tell me the current time.` | `generate_password` → `current_time` → `FINISH` |
| `Roll a dice and tell me the time.` | `roll_dice` → `current_time` → `FINISH` |
| `What time is it?` | `current_time` → `FINISH` |
| `Roll a dice, generate a password and tell me the time.` | 3 tools → `FINISH` |

---

# Part 1 — The Agent State 🧠

**Goal:** build the agent's **working memory**, the object that remembers the goal, which step we're on, what was done and what happened. Test it **alone**, before any AI.

> 💡 **Why state?** The LLM itself remembers nothing between calls (Day 2). An agent that runs many steps must **carry its memory along**. The state is a notebook the agent writes in after every step, and the planner **reads it** before choosing the next step.

## `state.py`

```python
def create_state(user_request, max_steps=5):
    return {
        "user_request": user_request,
        "current_step": 0,
        "max_steps": max_steps,
        "actions": [],
        "observations": [],
        "finished": False,
        "final_answer": ""
    }

def add_action(state, action):
    state["actions"].append(action)

def record_observation(state, action, observation):
    state["observations"].append(
        {
            "step": state["current_step"],
            "action": action,
            "observation": observation
        }
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

### Step-by-step explanation

**`create_state(user_request, max_steps=5)`**: a fresh notebook.

| Key | Starts as | Meaning |
|-----|-----------|---------|
| `user_request` | the goal | What the user asked |
| `current_step` | `0` | Which loop iteration we're on |
| `max_steps` | `5` | **Safety limit**: the most steps allowed |
| `actions` | `[]` | Tools already used, e.g. `["generate_password"]` |
| `observations` | `[]` | What each tool returned, with its step number |
| `finished` | `False` | Has the agent decided it's done? |
| `final_answer` | `""` | The reply for the user (filled at the end) |

**The helper functions**

| Function | What it does | When it's used |
|----------|--------------|----------------|
| `add_action(state, action)` | Appends the tool name to `actions` | After running a tool |
| `record_observation(state, action, observation)` | Appends `{"step", "action", "observation"}` to `observations` | After running a tool |
| `next_step(state)` | `current_step += 1` | End of each iteration |
| `can_continue(state)` | `True` only if **not finished AND** `current_step < max_steps` | Checked at the top of every loop |
| `finish(state, answer)` | Saves the answer, sets `finished = True` | When the planner says `FINISH` |

> 🛑 **`can_continue()` is the agent's brake.** Even if the LLM never says `FINISH`, the loop **must** stop after `max_steps`. Without this, a confused agent could run forever (and with a paid API, cost money forever).

> 💡 **Why functions instead of editing the dict directly?** Every change to the state goes through one small, named function. That makes the code readable (`next_step(state)` explains itself), keeps the changes consistent, and makes the state easy to test, which is exactly what `test_state.py` does.

## `test_state.py`

```python
from state import *

state = create_state(
    "Generate a password and tell me the current time."
)

print("Initial State")
print(state)

add_action(
    state,
    "generate_password"
)

record_observation(
    state,
    "generate_password",
    "Password : X#8Lm@4P"
)

next_step(state)

print("\nState After One Iteration")
print(state)

finish(
    state,
    "Password : X#8Lm@4P\nCurrent Time : 10:35 AM"
)

print("\nFinal State")
print(state)
```

### Step-by-step explanation

| Code | Simulates |
|------|-----------|
| `create_state("Generate a password and tell me the current time.")` | A new task arrives |
| `add_action(state, "generate_password")` | The agent chose and ran a tool |
| `record_observation(..., "Password : X#8Lm@4P")` | The tool's (fake) result is saved |
| `next_step(state)` | Move to step 1 |
| `finish(state, "Password : ...\nCurrent Time : 10:35 AM")` | The agent decides it's done |

No AI and no MCP are involved. We **pretend** to be the agent and check that the notebook updates correctly. It's the same "test small pieces first" rule as every previous day.

### 📤 Output — Part 1

#### `python test_state.py`
```
ervations': [], 'finished': False, 'final_answer': ''}

State After One Iteration
{'user_request': 'Generate a password and tell me the current time.', 'current_step': 1, 'max_steps': 5, 'actions': ['generate_password'], 'observations': [{'step': 0, 'action': 'generate_password', 'observation': 'Password : X#8Lm@4P'}], 'finished': False, 'final_answer': ''}

Final State
{'user_request': 'Generate a password and tell me the current time.', 'current_step': 1, 'max_steps': 5, 'actions': ['generate_password'], 'observations': [{'step': 0, 'action': 'generate_password', 'observation': 'Password : X#8Lm@4P'}], 'finished': True, 'final_answer': 'Password : X#8Lm@4P\nCurrent Time : 10:35 AM'}
(venv) 
```

**Observation:**
<!-- e.g. step went 0 → 1, actions/observations filled, finished False → True. -->

---

# Part 2 — The Complete Autonomous Agent 🔁

**Goal:** connect state + planner + executor + MCP tools in a **loop** that runs until the planner says `FINISH`.

## `server.py`: MCP server (from Day 8)

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
    # stdout is the MCP channel (stdio) - log to stderr only
    print("Starting MCP server..", file=sys.stderr)
    mcp.run()
```

The same three tools as Day 8: `current_time`, `roll_dice`, `generate_password`. `@mcp.tool()` exposes each function, and its **docstring** becomes the description the planner reads. The startup message prints to **stderr** (see *Changes from the Course Files*).

## `mcp_client.py`: MCP client helpers (from Day 8, in-memory)

```python
from fastmcp import Client

from server import mcp


async def connect():

    """
    Connect to the MCP Server (in-memory).
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

| Function | What it does |
|----------|--------------|
| `connect()` | `Client(mcp)` connects **in-memory** to the server object imported from `server.py` (Day 8 fix) |
| `disconnect(client)` | Closes the connection |
| `discover_tools(client)` | `tools/list` returns the tool objects (`.name`, `.description`) |
| `execute_tool(client, tool_name, arguments=None)` | `tools/call` runs a tool on the server and returns the result object |

## `planner.py`: the brain 🧭

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

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


def clean_action(reply, tools):

    """
    Turn the model's reply into a valid tool name or FINISH.
    """

    # Remove thinking text from models like qwen3
    if "</think>" in reply:
        reply = reply.split("</think>")[-1]

    reply = reply.strip().strip(" .`'\"\n")

    if reply.upper() == "FINISH":
        return "FINISH"

    for tool in tools:
        if tool.name in reply:
            return tool.name

    # Unknown reply -> stop safely
    return "FINISH"


def planner(state, tools):

    tool_descriptions = build_tool_descriptions(tools)

    done = state["actions"]

    not_used = [
        tool.name
        for tool in tools
        if tool.name not in done
    ]

    observations = "\n".join(
        f"- {o['action']} -> {o['observation']}"
        for o in state["observations"]
    ) or "None yet"

    prompt = f"""
You are an AI Planner.

Your job is to decide ONLY the next action.

User Request:
{state["user_request"]}

Already done:
{done if done else "Nothing yet"}

Results so far:
{observations}

Tools not used yet:
{not_used}

Available Tools:
{tool_descriptions}

Rules:

1. Split the user request into parts.
2. Check each part against "Already done".
3. Choose ONE tool for a part that is NOT done yet.
4. Never choose a tool from "Already done".
5. If every part of the request is done, return FINISH.
6. Return ONLY the tool name or FINISH. No explanation.

Next Action:
"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        temperature=0,
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

    reply = response.choices[0].message.content

    return clean_action(reply, tools)
```

### Step-by-step explanation

**`build_tool_descriptions(tools)`**: same as Day 8. It turns the tools discovered from the MCP server into text (`Tool: … Description: …`).

**`planner(state, tools)`**: the key difference from Day 8 is that the planner now receives the **whole state**, not just the question.

| Prompt section | Purpose |
|----------------|---------|
| `Your job is to decide ONLY the next action.` | One step at a time, not the whole plan. |
| `User Request: {state["user_request"]}` | The goal. |
| `Completed Actions: {state["actions"]}` | **What's already done.** This is how it avoids repeating steps. |
| `Previous Observations: {state["observations"]}` | **What happened so far**, used to judge what's still missing. |
| `Available Tools: {tool_descriptions}` | The menu, from MCP. |
| Rule 2: `Never repeat an action that has already been completed.` | Prevents loops like `current_time` → `current_time` → … |
| Rule 3: `Use the observations to decide what is still required.` | Reason from the results. |
| Rule 4: `If the user's request has been completely satisfied, return FINISH.` | **The stop signal.** This is what makes it autonomous: it decides when it's done. |
| Rules 5–6: `Return ONLY the tool name or FINISH.` / `Do not explain.` | A machine-readable reply. |

`.strip()` removes spaces and newlines, then the tool name (or `FINISH`) is returned.

### Day 8 planner vs Day 9 planner

| | Day 8 | Day 9 |
|---|---|---|
| Input | The user's question | The **whole state** (question + done actions + observations) |
| Output | One tool | The **next** tool, or `FINISH` |
| Called | Once | **Once per step**, repeatedly |
| Knows what's done | ❌ | ✅ |

## `executor.py`: the hands 🛠️

```python
from mcp_client import execute_tool


async def execute_action(action, client):

    result = await execute_tool(
        client,
        action
    )

    if hasattr(result, "content"):

        if result.content:

            return result.content[0].text

    return str(result)
```

| Code | Meaning |
|------|---------|
| `await execute_tool(client, action)` | Run the chosen tool on the MCP server (no arguments). |
| `hasattr(result, "content")` | Is this an MCP result object with a `content` list? |
| `if result.content:` | Is the list non-empty? |
| `return result.content[0].text` | Return **plain text** (e.g. `"4"`) instead of the whole object. This fixes Day 8's limitation #4 (raw object sent to the LLM). |
| `return str(result)` | Fallback: convert whatever came back into text. |

> 💡 The executor turns a messy result object into a **clean observation string** before it's saved in the state.

## `loop.py`: the heart ❤️🔁

```python
from state import (
    create_state,
    add_action,
    record_observation,
    next_step,
    can_continue,
    finish
)


async def run_agent_loop(
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):

    state = create_state(user_request)

    # The heart of our agent
    while can_continue(state):

        # 1. THINK - the planner decides the next action
        action = planner(state, tools)

        print("Planner Selected:", action)

        if action == "FINISH":

            answer = format_answer(state)

            finish(state, answer)

            break

        # Guard: don't run the same tool twice
        if action in state["actions"]:

            print("  -> already done, skipped")

            record_observation(
                state,
                action,
                "Skipped: already done. Choose a different tool or FINISH."
            )

            next_step(state)

            continue

        # 2. ACT - execute the action via MCP
        try:

            observation = await execute_action(
                action,
                client
            )

        except Exception as error:

            observation = f"Error: {error}"

        # 3. OBSERVE - remember what happened
        add_action(
            state,
            action
        )

        record_observation(
            state,
            action,
            observation
        )

        next_step(state)

    # Safety net: max_steps reached without FINISH
    if not state["finished"]:

        print("Max steps reached - writing answer from results so far.")

        finish(state, format_answer(state))

    return state
```

### Step-by-step explanation

| # | Code | Agent loop stage |
|---|------|------------------|
| 1 | `state = create_state(user_request)` | Open a fresh notebook. |
| 2 | `while can_continue(state):` | Keep going while **not finished** and **under `max_steps`**. |
| 3 | `action = planner(state, tools)` | 🧭 **THINK**: what's next? |
| 4 | `print("Planner Selected:", action)` | Show the decision, so you can watch the agent think. |
| 5 | `if action == "FINISH":` → `format_answer(state)` → `finish(...)` → `break` | 🏁 **Done**: write the final answer and leave the loop. |
| 6 | `observation = await execute_action(action, client)` | 🛠️ **ACT**: run the tool via MCP. |
| 7 | `add_action(state, action)` | Remember **what** was done. |
| 8 | `record_observation(state, action, observation)` | 👀 **OBSERVE**: remember **what happened**. |
| 9 | `next_step(state)` | Step counter +1, then back to the top. |
| 10 | `return state` | Hand the whole state (with `final_answer`) back to the runner. |

> 💡 **Dependency injection:** `planner`, `execute_action` and `format_answer` are **passed in as arguments** instead of imported inside `loop.py`. The loop doesn't care *which* planner or executor it gets, so you can swap in a test planner (or a different AI) without touching the loop. That's great for testing.

## `runner.py`: the starting point ▶️

```python
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio

from mcp_client import (
    connect,
    disconnect,
    discover_tools
)

from planner import planner
from executor import execute_action
from loop import run_agent_loop


load_dotenv()

llm = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def format_answer(state):

    results = "\n".join(
        f"- {o['action']}: {o['observation']}"
        for o in state["observations"]
        if not str(o["observation"]).startswith("Skipped")
    ) or "No results."

    prompt = f"""
The user asked:

{state["user_request"]}

Results:

{results}

Answer the user naturally.

Rules:
- Use ONLY the results above for facts. Never guess.
- Show every value (password, time, dice number) exactly as given.
- If a part of the request has no result, say it could not be done.
- Do not mention planning, state or tools.
"""

    response = llm.chat.completions.create(
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


async def main():

    mcp_client = await connect()

    tools = await discover_tools(mcp_client)

    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)

    user_request = input("\nUser : ")

    state = await run_agent_loop(
        user_request,
        planner,
        execute_action,
        format_answer,
        tools,
        mcp_client
    )

    print()
    print("Final Answer:")
    print(state["final_answer"])

    await disconnect(mcp_client)


if __name__ == "__main__":
    asyncio.run(main())
```

### Step-by-step explanation

**1. `format_answer(state)`: the final reply**

| Prompt part | Purpose |
|-------------|---------|
| `The user asked: …` | The goal. |
| `Actions performed: …` / `Observations: …` | Everything the agent did and found. |
| `Answer the user naturally.` | One friendly reply that combines **all** results. |
| `Do not mention internal planning / state / tools.` | The user sees an answer, not the machinery. |

**2. `main()`**

| Step | Code | Meaning |
|------|------|---------|
| 1 | `client = await connect()` | Connect to the MCP server. |
| 2 | `tools = await discover_tools(client)` | Get the tool list, then print the names. |
| 3 | `user_request = input("\nUser : ")` | Ask for the goal. |
| 4 | `await run_agent_loop(user_request, planner, execute_action, format_answer, tools, client)` | **Run the autonomous loop**, passing in all the parts. |
| 5 | `print(state["final_answer"])` | Show the result. |
| 6 | `await disconnect(client)` | Clean up. |

> ⚠️ **Name clash (same as Day 8):** the module-level `client` is the **OpenAI (LLM)** client, used by `format_answer()`. Inside `main()`, `client` is the **MCP** client. It works, but `llm` and `mcp_client` would be clearer names.

## `test_state.py` (P2)

```python
from state import *

state = create_state(
    "Generate a password and tell me the current time."
)

print("Initial State")
print(state)

add_action(
    state,
    "generate_password"
)

record_observation(
    state,
    "generate_password",
    "Password : X#8Lm@4P"
)

next_step(state)

print("\nState After One Iteration")
print(state)

finish(
    state,
    "Password : X#8Lm@4P\nCurrent Time : 10:35 AM"
)

print("\nFinal State")
print(state)
```

The same test as P1, with the import fixed (`from state import *`).

### 📤 Output — Part 2

#### `python runner.py` → `Generate a password and tell me the current time.`
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

User : Generate a password and tell me the current time.
Planner Selected: current_time
Planner Selected: generate_password
Planner Selected: FINISH

Final Answer:
You've already got a password: 7@B?I@lRWZ;b.

The current time is 05-11-2026 18:22:49.
```

#### `python runner.py` → `Roll a dice and tell me the time.`
```
roll_dice
generate_password

User : Roll a dice and tell me the time.
Planner Selected: roll_dice
Planner Selected: current_time
Planner Selected: current_time
Planner Selected: FINISH

Final Answer:
I rolled a dice and the result is 4. The current time is 03-11-2026 17:24:12.
```

#### `python runner.py` → `What time is it?` (single step)
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

User :  What time is it?
Planner Selected: current_time
Planner Selected: current_time
Planner Selected: FINISH

Final Answer:
It's now 5:46 PM.
```

#### `python runner.py` → `Roll a dice, generate a password and tell me the time.` (3 steps)
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

User : Roll a dice, generate a password and tell me the time.
Planner Selected: roll_dice
Planner Selected: current_time
Planner Selected: generate_password
Planner Selected: roll_dice
  -> already done, skipped
Planner Selected: current_time
  -> already done, skipped
Max steps reached - writing answer from results so far.

Final Answer:
It looks like we've got some interesting results here!

Let's start with the dice roll. It looks like we got a 1. Not the most exciting number, but it's what we've got!

Next up, we've got the current time. It's currently 03-11-2026 17:37:07. That's a specific time, so we can work with that.

And finally, we've got a password. It's a bit... unusual. The password is ]'57[,1QPuN. I'm not sure what to make of it, butit's definitely a unique password!

So, that's what we've got. A dice roll of 1, a specific current time, and a rather... interesting password.
(venv) 
```

**Observation:**
<!-- e.g. The planner chose a different number of steps for each request and stopped by itself with FINISH. -->

---

## 🔍 Day 8 vs Day 9

| | Day 8 — MCP agent | Day 9 — Autonomous agent |
|---|---|---|
| Tools per request | 1 | As many as needed |
| Loop | ❌ | ✅ `while can_continue(state)` |
| Memory of the task | ❌ | ✅ Agent state |
| Knows when to stop | Always after 1 step | Planner returns `FINISH` |
| Safety limit | — | `max_steps = 5` |
| LLM calls per request | 2 | (steps + 1) planner + 1 answer |
| Code structure | 1 big `agent.py` | 6 small files, one job each |

---

## ⚠️ Known Limitations of This Code / Improvements

1. **No cleaning of the planner's reply.** `if action == "FINISH"` and `call_tool(action)` need an **exact** match. `Finish`, `FINISH.`, `` `current_time` `` or qwen3's `<think>...</think>` → `FINISH` isn't recognised, or `call_tool` crashes with an unknown tool. Reuse Day 7's cleaner:
   ```python
   def clean_action(reply, tools):
       if "</think>" in reply:
           reply = reply.split("</think>")[-1]
       reply = reply.strip().strip(" .`'\"\n")
       if reply.upper() == "FINISH":
           return "FINISH"
       names = [t.name for t in tools]
       for name in names:
           if name in reply:
               return name
       return "FINISH"        # unknown → stop safely
   ```
   …and in `planner()`: `return clean_action(response.choices[0].message.content, tools)`.
2. **Hitting `max_steps` gives an empty answer.** If the planner never says `FINISH`, the loop ends after 5 steps with `final_answer = ""`, and `runner.py` prints nothing. Fix: after the loop, `if not state["finished"]: finish(state, format_answer(state))`.
3. **A tool error crashes the agent.** `execute_action` has no `try/except`. A bad tool name stops everything. Fix: catch the error and record it as an observation (`"Error: unknown tool"`), so the planner can recover.
4. **"Never repeat" blocks valid requests.** *"Roll the dice twice"* needs `roll_dice` two times, but rule 2 forbids it. Better rule: *"Don't repeat an action unless the request needs it more than once."*
5. **No tool arguments.** `execute_tool(client, action)` always sends `{}`, so *"a 20-character password"* still gives 12. Next step: have the planner return JSON, e.g. `{"tool": "generate_password", "arguments": {"length": 20}}`.
6. **The planner can finish too early,** for example `FINISH` after only one of two tasks. Add a rule like *"Check every part of the request against the observations before returning FINISH."*
7. **Observations are sent as raw Python lists/dicts** (`[{'step': 0, 'action': ...}]`). Readable lines (`Step 0 – generate_password → X#8Lm…`) help small models reason better.
8. **The password passes through the LLM** in `format_answer()`, and the model may re-type it wrongly (Day 7 lesson). Print exact values directly as well.
9. **The date is ambiguous:** `%d-%m-%Y` can be read as month-first (Day 7 lesson). Use `"%d %B %Y, %H:%M:%S"`.
10. **One request per run.** There's no chat loop. Wrap the input + `run_agent_loop` in `while True` with `quit`.
11. **No human approval.** Fine for safe tools, but before adding risky tools (delete, send, pay), ask the user to confirm each action.
12. **The sync LLM calls run inside async code** and block the event loop. Use `AsyncOpenAI` for concurrent agents.

---

## 🛠️ Troubleshooting

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `ModuleNotFoundError: No module named 'Day09'` (P2 `test_state.py`) | Wrong import in the course file | `from state import *` (fixed above) |
| `ModuleNotFoundError: No module named 'state'` / `'server'` | Running from the wrong folder | `cd` into **`Day09_P2/agent`** first |
| `MCPError: Connection closed` | stdio subprocess fails on this PC | Use the in-memory `mcp_client.py` above (Day 8 #5) |
| `Failed to parse JSONRPC message` | `print()` to stdout in `server.py` | `file=sys.stderr` (fixed above) |
| `Unknown tool: ...` | The planner returned extra text | `llama3.2` + `clean_action()` (limitation #1) |
| `Planner Selected:` repeats until it stops, then the answer is empty | The planner never returned an exact `FINISH` | Limitations #1 and #2 |
| Traceback shows `...\Python310\...` | The venv isn't really active | `source venv/Scripts/activate`, then check `which python` (Day 8 #4) |

---

## ✅ Key Takeaways

- An **autonomous agent** gets a **goal** and keeps choosing and doing actions **by itself** until it's done.
- **Agent loop = Think (planner) → Act (executor) → Observe (state) → repeat**, until `FINISH` or `max_steps`.
- The **state** is the agent's working memory, and the planner reads it before every step.
- Ask the planner for **only the next step**, not the whole plan. It adapts to results as they come.
- **Always have a brake** (`max_steps`). An agent must never be able to run forever.
- **Small files with one job each** (state, planner, executor, loop, runner) make the agent easy to test and change.
- Autonomy is powerful but risky. **Guardrails, error handling and human approval** matter as much as the AI.

---

