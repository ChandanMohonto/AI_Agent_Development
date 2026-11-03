# Day 10 — Advanced Agent Planning: Task Decomposition 🗂️🤖

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
| Day 09 | Autonomous agent — loop: next action → act → observe |
| **Day 10** | **Advanced planning — break the goal into tasks first, then complete them one by one** |

---

## 🎯 Goal of Day 10

On Day 9 the agent only ever asked **"What's the next action?"** It had **no plan**, so it wandered: it repeated tools, forgot parts of the request, and stopped too early (we saw all three in real runs).

On Day 10 the agent first **makes a plan**, a to-do list of small tasks, and then works through it, ticking each task off:

```
"Get the current time, generate a secure password, and explain Python."

                     │  1. DECOMPOSE (plan first)
                     ▼
   ☐ Get the current time
   ☐ Generate a secure password
   ☐ Explain Python
                     │  2. EXECUTE task by task
                     ▼
   ☑ Get the current time        → current_time       → 03-11-2026 14:05:10
   ☑ Generate a secure password  → generate_password  → k#9Lp!2xQ@7m
   ☑ Explain Python              → (no tool needed)
                     │  3. ALL DONE → ANSWER
                     ▼
   "The time is 14:05:10. Your password is k#9Lp!2xQ@7m.
    Python is a popular, easy-to-read programming language…"
```

---

## 🤔 What Is Task Decomposition?

**Task decomposition** means **breaking a big goal into smaller, ordered tasks**, each small enough to be done in one step.

### 🧑‍🍳 Real-life scenario: planning a birthday party

You ask a friend: *"Organise a birthday party on Saturday."*

**❌ Friend A (Day 9 style, "next action" only):**
They keep asking themselves *"What should I do now?"*. They buy balloons, buy balloons again, forget the cake, and call it done once the decorations are up. 🎈🎈🎈 No cake. 😬

**✅ Friend B (Day 10 style, plan first):**
They write a checklist first:

```
☐ Book a venue
☐ Invite guests
☐ Order the cake
☐ Buy decorations
```

Then they do **one item at a time**, **tick it off**, and only say *"Party ready!"* when **every box is ticked**. Nothing is forgotten, nothing is repeated, and anyone can see the progress.

**Friend B is the Day 10 agent.**

### 🧪 Real-life scenario 2: a QA release sign-off

*"Prepare the release sign-off for v2.3."*

```
☐ Run the regression suite          → test runner tool
☐ Collect open critical bugs        → bug tracker tool
☐ Check test coverage               → coverage tool
☐ Write the sign-off summary        → no tool (the AI writes it)
```

A QA lead does exactly this every release: **split the goal into a checklist, assign the right tool to each item, track status, and report when everything is done.**

---

## ⚙️ How It Works: Plan-and-Execute

Day 10 uses a pattern called **Plan-and-Execute**: plan everything up front, then execute step by step.

```
User request
     │
     ▼
┌──────────────────────────┐
│ 1. TASK DECOMPOSER (LLM) │  task_planner.py
│ goal → list of tasks     │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│       AGENT STATE        │  state.py
│ tasks: [{task, status}]  │  ← pending / completed
│ actions, observations,   │
│ results, step, finished  │
└────────────┬─────────────┘
             ▼
     ┌── all tasks completed? ──── yes ──────────────┐
     │ no                                            │
     ▼                                               │
┌──────────────────────────┐                         │
│ 2. STATE-AWARE PLANNER   │  planner.py             │
│ picks ONE pending task   │                         │
│ + the best tool          │                         │
│ → "TASK: …  TOOL: …"     │                         │
└────────────┬─────────────┘                         │
             ▼                                       │
┌──────────────────────────┐                         │
│ 3. EXECUTOR (MCP)        │  executor.py            │
│ runs the tool            │                         │
└────────────┬─────────────┘                         │
             ▼                                       │
   save observation, mark task ☑, step +1            │
             │                                       │
             └── step < max_steps? → loop again      │
                                                     ▼
                                  ┌──────────────────────────┐
                                  │ 4. ANSWER GENERATOR (LLM)│  answer.py
                                  │ all results → one reply  │
                                  └──────────────────────────┘
```

### Day 9 vs Day 10

| | Day 9 — next-action agent | Day 10 — plan-and-execute agent |
|---|---|---|
| Plans ahead? | ❌ Only decides the next step | ✅ Makes the full task list first |
| Planner chooses | A tool | **A task + a tool** |
| Progress tracking | List of actions done | Each task is **pending / completed** |
| Who decides "finished"? | The LLM says `FINISH` (unreliable) | **Code** checks `all_tasks_completed()` |
| Tasks with no tool ("explain Python") | Not handled | `TOOL: none` → answered by the LLM |
| Real runs we saw | Repeats, early finish, empty answers | Clear checklist, visible progress |
| Pattern name | ReAct (reason + act) | Plan-and-Execute |

---

## ✅ Benefits of Task Decomposition

| Benefit | Explanation |
|---------|-------------|
| 🗺️ **Big picture first** | The agent knows *everything* it must do before starting, so parts are rarely forgotten. |
| 👀 **Visible progress** | `☑ 2 / 3 tasks done`: humans can see and check the plan. |
| ✅ **Reliable finish** | "Done" is decided by **code** (all tasks completed), not by an LLM guessing `FINISH`. |
| 🎯 **Simpler decisions** | Each step is a small question: *"which tool for THIS task?"* That's easier for small models. |
| 🧩 **Mixed tasks** | Tool tasks (time, password) and knowledge tasks (explain Python) in one request. |
| 🐞 **Easier debugging** | If the answer is wrong, check: was the **plan** wrong, the **tool choice** wrong, or the **tool result** wrong? |
| 🧑‍💼 **Human review** | The plan can be shown for approval **before** anything runs, which matters for risky tasks. |

## ⚠️ Limitations

| Limitation | Explanation |
|------------|-------------|
| 🧱 **Bad plan = bad everything** | If decomposition misses a task or adds a wrong one, execution follows the wrong plan. |
| 🧊 **Static plan** | The plan is made once. If a result changes what's needed, it isn't re-planned (advanced agents *re-plan*). |
| 🔤 **Text matching is fragile** | A task is ticked off only if the planner copies its wording **exactly**. If it rephrases, the task stays pending. |
| 🐢💸 **More LLM calls** | 1 decompose + 1 per task + 1 answer, so it's slower and costs more than a one-shot answer. |
| 🪓 **Over- or under-splitting** | *"Get the time"* might become 3 tasks, or *"time and password"* stay as 1. |
| 🔗 **No dependencies** | Tasks run in a fixed order. *"Use the time in the password"* (task 2 needs task 1's output) isn't modelled. |
| 🔁 **Can still loop** | A wrong tool, or a task that never completes, uses up steps. `max_steps` is still essential. |

## 🌍 Where Task Decomposition Is Used

| Area | Example |
|------|---------|
| 💻 **Coding agents** | "Add login" → create model → add route → write tests → run tests → fix |
| 🧪 **QA automation** | "Test checkout" → list scenarios → generate test cases → run → report bugs |
| 🔬 **Research agents** | "Compare 3 laptops" → search each → extract specs → build a table → summarise |
| 🎧 **Customer support** | "Refund my order" → verify customer → check policy → issue refund → send email |
| 📊 **Data analysis** | "Sales report" → load data → clean → aggregate → chart → write insights |
| 🗓️ **Project management tools** | AI that turns a feature request into tickets/sub-tasks |

---

## 🧩 The 2 Parts at a Glance

| Part | Course lessons | What we build | Files |
|------|----------------|---------------|-------|
| **P1** | 123–125 | The **task decomposer**: goal → task list, tested alone | `task_planner.py`, `test_task_planner.py` |
| **P2** | 126–133 | The **complete Day 10 agent**: tasks in state, state-aware planner, MCP execution, agent loop, answer generator, runner | all files below |

---

## 📁 Folder Structure

```
Day_10_Advanced-Planning/
├── README.md
├── Day10_P1/
│   ├── task_planner.py        # decompose_task(): goal → tasks
│   └── test_task_planner.py   # test the decomposer alone
└── Day10_P2/
    ├── task_planner.py        # same as P1
    ├── test_task_planner.py   # same as P1
    ├── state.py               # agent state, now with tasks + status
    ├── planner.py             # state-aware planner: TASK + TOOL
    ├── executor.py            # runs the tool via MCP
    ├── loop.py                # decompose → loop → finish
    ├── answer.py              # answer generator
    ├── runner.py              # ▶️ START HERE
    ├── server.py              # MCP server: 3 tools (from Day 8)
    └── mcp_client.py          # MCP client (in-memory, from Day 8)
```

> No `agent/` subfolder this time: the files sit directly in `Day10_P1` and `Day10_P2`.

### How the files connect

```
runner.py
 ├── mcp_client.py ──► server.py          (connect, discover tools)
 ├── answer.py        → format_answer()   (passed into the loop)
 ├── planner.py       → planner()         (passed into the loop)
 ├── executor.py      → execute_action()  (passed into the loop)
 │     └── mcp_client.py ──► server.py
 └── loop.py          → run_agent_loop()
       ├── task_planner.py → decompose_task()
       └── state.py        → create/update state
```

---

## 🔧 Changes from the Course Files

The course code has the **same problems we hit on Days 8–9**, plus one new crash. **The code in this README is the fixed version.** Every change is marked with a `# FIX:` comment in the code.

| File | Problem in the course version | Fix |
|------|-------------------------------|-----|
| `server.py` | `print()` to stdout breaks the MCP stdio channel | Print to `stderr` (Day 8) |
| `mcp_client.py` | `Client("server.py")` (stdio) fails with `Connection closed` on this PC | In-memory `Client(mcp)` (Day 8) |
| `executor.py` | 💥 **"Explain Python" crashes the agent.** No tool fits, so the planner returns some name, and `call_tool` raises `ToolError: Unknown tool` | `TOOL: none` → "No tool needed" observation; `try/except` turns tool errors into `Error: …` observations |
| `planner.py` | No instruction for tasks without a tool | Added rule 7b: `TOOL: none` |
| `loop.py` | Hitting `max_steps` → **empty final answer** (Day 9 bug) | Always generate an answer after the loop |
| `loop.py` | Tool name with backticks/quotes/dots → unknown tool | Clean the tool name in `parse_decision()` |
| `loop.py` | `max_steps=5` leaves no room for retries | `max_steps=8` |
| `task_planner.py` | Models add bullets/numbers, or `<think>` text, which become fake tasks | Strip bullets, numbers and `<think>` blocks |
| `answer.py` | The answer LLM may invent or hide values (Day 9: invented time, hid password) | Rules: use observations as facts, show values exactly |
| `planner.py`, `task_planner.py`, `answer.py` | Different results every run | `temperature=0` |

> ✅ The fixed loop was tested with a fake planner: a mixed request (time + password + "explain Python") completed all 3 tasks, wrong tool names were caught as errors without crashing, and `max_steps` still produced an answer. The original `call_tool("none")` was confirmed to raise `ToolError: Unknown tool: none`.

---

## ⚙️ Setup

Same as Days 8–9: shared venv, root `.env`, `fastmcp<3`. Nothing new to install.

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
which python                 # must show .../AI_Agent_Journy/venv/Scripts/python
rm -f Day_10_Advanced-Planning/Day10_P*/.env      # use the shared root .env
```

> **Model tip:** the zip's `.env` uses **`qwen3:1.7b`**, which is very small and a "thinking" model. It often breaks the strict `TASK:` / `TOOL:` format. **`llama3.2`** in the root `.env` is recommended:
> ```env
> MODEL=llama3.2
> ```

---

## ▶️ How to Run: Which File First?

> Run each script from **inside its part folder** (imports like `from state import ...` look in the current folder).
> You **don't** run `server.py` yourself.

| # | Folder | Command | What it does | Expected |
|---|--------|---------|--------------|----------|
| 1 | `Day10_P1` | `python test_task_planner.py` | Decomposes a sample request, with no tools and no loop | A `Task Plan` list of 3 tasks |
| 2 | `Day10_P2` | `python runner.py` | ▶️ **The complete Day 10 agent** | Task Plan → Steps → `Final Answer` |

```bash
cd "/d/AI Agents/AI_Agent_Journy/Day_10_Advanced-Planning/Day10_P1"
python test_task_planner.py

cd ../Day10_P2
python runner.py
```

**Requests to try in `runner.py`:**

| Request | Expected plan |
|---------|---------------|
| `Get the current time, generate a secure password, and explain Python.` | 3 tasks: `current_time`, `generate_password`, `none` |
| `Roll a dice, generate a password and tell me the time.` | 3 tool tasks |
| `What time is it?` | 1 task |
| `Explain what an API is.` | 1 task, `TOOL: none` |

---

# Part 1 — The Task Decomposer 🗂️

**Goal:** an LLM function that turns one goal into an **ordered list of small tasks**, tested alone.

## `task_planner.py`

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
```

### Step-by-step explanation

| Code | Meaning |
|------|---------|
| `load_dotenv()` + `OpenAI(...)` | The LLM client (Ollama), same as every day. |
| `def decompose_task(user_request):` | Input: the user's goal. Output: a **Python list of task strings**. |
| Prompt `Break the user's request into smaller tasks.` | The job. |
| Rule 1 `Create only necessary tasks.` | Prevents over-splitting. |
| Rule 2 `Put tasks in execution order.` | The list is the order they'll run in. |
| Rule 3 `Each task should be a short action.` | E.g. "Get the current time". |
| Rules 4–6 `one task per line`, `Do not number`, `Do not explain` | A format that's easy to split into a list. |
| `temperature=0` | **FIX:** the same request gives (almost) the same plan every time. |
| `if "</think>" in result:` | **FIX:** drop qwen3's thinking text, so it doesn't become "tasks". |
| `for line in result.splitlines():` | One line = one task. |
| `line.strip().lstrip("-*•").strip()` | **FIX:** remove bullet symbols the model may still add. |
| `re.sub(r"^\d+[.)]\s*", "", line)` | **FIX:** remove numbering like `1.` or `2)`. `^\d+` = digits at the start, `[.)]` = a dot or bracket, `\s*` = spaces. |
| `if line: tasks.append(line)` | Skip empty lines. |

**Example:**

```
LLM reply:                      →   tasks list:
<think>…</think>                    ["Get the current time",
1. Get the current time              "Generate a secure password",
- Generate a secure password         "Explain Python"]
* Explain Python
```

## `test_task_planner.py`

```python
from task_planner import decompose_task


user_request = (
    "Get the current time, generate a secure password, and explain Python."
)


tasks = decompose_task(user_request)


print("\nTask Plan")
print("---------")

for task in tasks:
    print("-", task)
```

Calls the decomposer on a mixed request (2 tool tasks + 1 knowledge task) and prints the plan. No MCP and no loop.

### 📤 Output — Part 1

#### `python test_task_planner.py`
```
$ python test_task_planner.py

Task Plan
---------
- Get current time
- Generate secure password
- Explain Python basics
- Create Python documentation
- Install Python on user's device
- Write Python code example
- Test Python code
- Provide user with Python reference materials
(venv) 
```

**Observation:**
<!-- e.g. 3 tasks in the right order; run it twice to check the plan stays the same. -->

---

# Part 2 — The Complete Day 10 Agent 🤖

## `state.py`: agent state with tasks

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
        "finished": False,
        "final_answer": ""
    }


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

### What's new compared to Day 9

| Key / function | Meaning |
|----------------|---------|
| `"tasks": []` | The **plan**: a list of `{"task": "...", "status": "pending"}` |
| `"current_task": None` | The task being worked on right now |
| `"results": []` | Intermediate results (tool outputs and failure notes) |
| `add_task(state, task)` | Add a task as **pending** ☐ |
| `complete_task(state, task)` | Mark a task **completed** ☑, with tolerant matching (see below) |
| `get_pending_tasks(state)` | List the tasks still to do |
| `all_tasks_completed(state)` | `True` only when **every** task is completed. **Code** decides "done", not the LLM |

**Tolerant matching in `complete_task()`:** the planner might write `generate_password` while the task says `Generate password`. Both are **normalised** before comparing:

```
"Generate password"  → .strip().lower().replace("_"," ") → "generate password"
"generate_password"  → .strip().lower().replace("_"," ") → "generate password"   ✅ match
```

> ⚠️ It still needs the **same words**. "Create a password" ≠ "Generate password". That's why the planner is told to copy the task **exactly**.

**`all_tasks_completed()` with an empty list returns `False`.** With no tasks, it doesn't claim "all done". (`all([])` would be `True` in Python, so this check prevents a false "done".)

Unchanged from Day 9: `add_action`, `record_observation`, `next_step`, `can_continue` (the brake) and `finish`.

## `planner.py`: the state-aware planner 🧭

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

6. Use previous observations and results.

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

### Step-by-step explanation

The planner now sees the **whole plan with progress**, and must answer with **a task and a tool**.

| Prompt section | Purpose |
|----------------|---------|
| `Tasks:` | The full plan with statuses. |
| `Pending Tasks:` (list comprehension) | **Only the unfinished tasks**, computed in Python, so the LLM doesn't have to work it out. |
| `Completed Actions:` / `Observations:` / `Intermediate Results:` | What's done and what happened. |
| `Available Tools:` | The tool menu from MCP. |
| Rules 1–4 | Pick **one pending** task, copy its wording **exactly**, never a completed one. |
| Rules 5–7 | Pick the best tool, use previous results, and reconsider if something failed. |
| Rule 7b `TOOL: none` | **FIX:** a safe answer for tasks no tool can do ("Explain Python"). |
| Rule 8 `FINISH` | No pending tasks → finish. |
| Rule 9 | **Strict 2-line format**: `TASK: <exact task>` / `TOOL: <tool_name>` |
| `temperature=0` | **FIX:** consistent decisions. |

**Example reply:**

```
TASK: Generate a secure password
TOOL: generate_password
```

### Day 9 planner vs Day 10 planner

| | Day 9 | Day 10 |
|---|---|---|
| Output | `current_time` | `TASK: Get the current time` + `TOOL: current_time` |
| Knows the plan | ❌ | ✅ Full task list + pending list |
| Chooses | A tool | A **task**, then the **tool** for it |

## `executor.py`: running the tool 🛠️

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

| Code | Meaning |
|------|---------|
| `if action.lower() == "none":` | **FIX:** a knowledge task. Don't call MCP; return a note so the answer generator handles it. |
| `try: … await execute_tool(client, action)` | Run the tool on the MCP server. |
| `except Exception as error: return f"Error: {error}"` | **FIX:** an unknown tool becomes an **observation** instead of a crash. The loop sees `Error…`, leaves the task pending and lets the planner retry. |
| `result.content[0].text` | Extract plain text from the MCP result (same as Day 9). |
| `state` parameter | Passed in for future use (e.g. tool arguments from the state); not used yet. |

## `loop.py`: decompose → loop → finish 🔁

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

    return state
```

### Step-by-step explanation

**`parse_decision(decision)`** turns the planner's text into `(task, tool)`:

| Planner reply | Result |
|---------------|--------|
| `TASK: Get the current time` ⏎ `TOOL: current_time` | `("Get the current time", "current_time")` |
| `TASK: Get the current time TOOL: current_time` (one line) | Split on `TOOL:` → same result |
| `TOOL: \`current_time\`.` | **FIX:** cleaned to `current_time` |
| Missing `TASK:` or `TOOL:` | `(None, …)` → "Invalid planner decision", and the step is used up |

`line[5:]` skips the first 5 characters (`TASK:` and `TOOL:` are both 5 long). `split("TOOL:", 1)` splits only at the **first** `TOOL:`.

**`run_agent_loop(...)`**

| # | Stage | Code |
|---|-------|------|
| 1 | Create state | `create_state(user_request, max_steps=8)` (**FIX:** was 5) |
| 2 | 🗂️ **Decompose** | `decompose_task(user_request)` → `add_task()` for each → print the **Task Plan** |
| 3 | 🔁 Loop | `while can_continue(state):` |
| 4 | ✅ **Code-level finish check** | `if all_tasks_completed(state):` → `format_answer` → `finish` → `break` |
| 5 | 🧭 Ask the planner | `decision = planner(state, tools)` |
| 6 | LLM finish | `if decision == "FINISH"` → answer → `break` |
| 7 | Parse | `task, tool = parse_decision(decision)`; if invalid → note it, step +1, `continue` |
| 8 | 🛠️ Execute | `observation = await execute_action(tool, state, client)` |
| 9 | 👀 Record | `add_action`, `record_observation`, `add_result` |
| 10 | ☑ Tick off | If the observation doesn't start with `error` → `complete_task()` → print `completed`. Otherwise add "The previous action failed…" so the planner retries. |
| 11 | Next | `next_step(state)` |
| 12 | 🛟 **Safety net** | **FIX:** after the loop, if not finished → still `format_answer()` |

> 💡 **Two ways to finish:** the **code** check (`all_tasks_completed`) runs **before** asking the planner, so even if the LLM never says `FINISH`, the agent stops as soon as the checklist is complete. That's the big reliability gain over Day 9.

## `answer.py`: the answer generator 💬

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

Tasks:
{state["tasks"]}

Actions:
{state["actions"]}

Observations:
{state["observations"]}

Intermediate Results:
{state["results"]}

Give the user a natural and concise answer.

Rules:
- Use the observations as facts. Never invent times, numbers or passwords.
- Show every value (time, password, dice number) exactly as given.
- For a task whose observation says "No tool needed",
  answer it briefly from your own knowledge.
- If a task failed, say it could not be done.

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

| Prompt part | Purpose |
|-------------|---------|
| `User asked` / `Tasks` / `Actions` / `Observations` / `Intermediate Results` | Everything the agent did. |
| `Give the user a natural and concise answer.` | One friendly reply. |
| **FIX rules:** observations are facts, show values exactly, answer "No tool needed" tasks from knowledge, report failures | Prevents the Day 9 problems (invented time, hidden password) and covers "explain Python". |
| `Do not mention: planner, agent loop, MCP, …` | The user sees the result, not the machinery. |

## `runner.py`: the starting point ▶️

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


async def main():

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

| Step | Code |
|------|------|
| 1 | `connect()` → MCP server |
| 2 | `discover_tools()` → print the tool names |
| 3 | `input("User : ")` → the goal |
| 4 | `run_agent_loop(user_request, planner, execute_action, format_answer, tools, client)` → the components are **passed in** (dependency injection, as on Day 9) |
| 5 | Print `Final Answer` |
| 6 | `disconnect()` |

> Each LLM-using file (`task_planner.py`, `planner.py`, `answer.py`) creates its **own** `OpenAI` client. That works, but one shared `llm.py` would be cleaner.

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
    # FIX: stdout is the MCP channel - log to stderr only
    print("Starting MCP server..", file=sys.stderr)
    mcp.run()
```

## `mcp_client.py`: MCP client (from Day 8, in-memory)

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

See Day 8 for a full explanation of both files and why the client is in-memory.

### 📤 Output — Part 2

#### `Get the current time, generate a secure password, and explain Python.`
```

Available Tools
----------------
current_time
roll_dice
generate_password

User : Get the current time, generate a secure password, and explain Python.

Task Plan
---------
- Get current time
- Generate secure password
- Explain Python basics
- Create Python documentation
- Install Python on user's device
- Write Python code example
- Test Python code
- Provide user with Python reference materials

--- Step 1 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Get current time
TOOL: current_time

The current_time tool is specifically designed to return the current date and time, making it the most suitable tool for this task.
Observation: 03-11-2026 18:46:57
completed

--- Step 2 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Generate secure password
TOOL: generate_password

The generate_password tool is specifically designed to generate secure passwords, which matches the task of generating a secure password.
Observation: 6:q$c6xBXat/
completed

--- Step 3 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Install Python on user's device
TOOL: generate_password

However, I noticed that the task "Install Python on user's device" is not a task that can be completed with the available tools. The tool "generate_password" is used to generate a secure password, not to install Python.

Let me try again:

TASK: Install Python on user's device
TOOL: none

This is because there is no available tool that can be used to install Python on a user's device.
Observation: No tool needed. Answer this task from general knowledge.
completed

--- Step 4 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Explain Python basics'
TOOL: generate_password

Explanation: Since the task is to explain Python basics, which is a complex topic that requires a detailed explanation, thetool 'generate_password' is not suitable for this task. However, the tool 'generate_password' is available, and it is not clear if it can be used for this task. Therefore, I will select 'generate_password' as the tool, but I will reconsider this decision if a more suitable tool is found.

Please note that this decision may not be the best one, and I will reconsider it if a more suitable tool is found.

--- Step 5 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Write Python code example
TOOL: generate_password

However, I realize that the task "Write Python code example" is not a good fit for the tool "generate_password". The tool "generate_password" is used to generate a secure password, not to write code.

Upon re-evaluation, I recommend the following:

TASK: Write Python code example
TOOL: none

This is because there is no available tool that can directly assist with writing a Python code example. The task requires amore creative and problem-solving approach, which is not currently supported by the available tools.
Observation: No tool needed. Answer this task from general knowledge.
completed

--- Step 6 ---
Planner Decision:
Based on the provided information, I will select the next unfinished task and the best tool to complete it.

Task: 'Explain Python basics'
TOOL: generate_password

Explanation: Since the task 'Explain Python basics' cannot be completed with a single tool, I will select 'generate_password' as the tool. However, this seems counterintuitive, as generating a password does not help explain Python basics. Upon reevaluation, I realize that I should have selected 'TOOL: none' for this task, as there is no tool available to explain Pythonbasics.

--- Step 7 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Explain Python basics
TOOL: generate_password

However, I realize that the tool 'generate_password' is not suitable for explaining Python basics. Therefore, I will reconsider the task.

TASK: Explain Python basics
TOOL: none

This decision is based on the fact that there is no available tool that can explain Python basics.
Observation: No tool needed. Answer this task from general knowledge.
completed

--- Step 8 ---
Planner Decision:
Based on the available tools and the pending tasks, I recommend the following:

TASK: Test Python code
TOOL: generate_password

However, I realize that the task "Test Python code" is not a good fit for the tool "generate_password". The tool "generate_password" is used to generate a secure password, not to test Python code.

Upon re-evaluation, I recommend the following:

TASK: Test Python code
TOOL: roll_dice

However, I still think that "Test Python code" is not a good fit for the tool "roll_dice". The tool "roll_dice" is used to roll a six-sided dice, not to test Python code.

After re-evaluating the available tools, I realize that I need to use the "none" tool for this task. The task "Test Python code" is not a good fit for any of the available tools.

Therefore, I recommend the following:

TASK: Test Python code
TOOL: none

However, I still need to select a pending task. After re-evaluating the available tasks, I recommend the following:

TASK: Provide user with Python reference materials
TOOL: none

This task is not a good fit for any of the available tools. Therefore, I recommend using the "none" tool.

However, I still need to select another pending task. After re-evaluating the available tasks, I recommend the following:

TASK: Create Python documentation
TOOL: roll_dice

This task is not a good fit for the tool "roll_dice". The tool "roll_dice" is used to roll a six-sided dice, not to create Python documentation.

Therefore, I recommend the following:

TASK: Create Python documentation
TOOL: generate_password

However, I realize that the task "Create Python documentation" is not a good fit for the tool "generate_password". The tool"generate_password" is used to generate a secure password, not to create Python documentation.

After re-evaluating the available tools, I realize that I need to use the "none" tool for this task.

Therefore, I recommend the following:

TASK: Create Python documentation
TOOL: none

However, I still need to select another pending task. After re-evaluating the available tasks, I recommend the following:

TASK: Provide user with Python reference materials
TOOL: none

This task is not a good fit for any of the available tools. Therefore, I recommend using the "none" tool.

Since there are no more pending tasks, I recommend the following:

FINISH
Observation: No tool needed. Answer this task from general knowledge.
completed

Max steps reached - answering with results so far.

Final Answer
------------
Let's get started with the tasks you've requested.

First, the current time is: 03-11-2026 18:46:57

Next, a secure password is: 6:q$c6xBXat/

Now, let's talk about Python. Python is a high-level, interpreted programming language that is widely used for various purposes such as web development, scientific computing, and data analysis. It's known for its simplicity, readability, and ease of use, making it a great language for beginners and experts alike.

If you're new to Python, I can provide you with some reference materials or code examples to get you started. Just let me know!
```

#### `Roll a dice, generate a password and tell me the time.`
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

User : Roll a dice, generate a password and tell me the time

Task Plan
---------
- Roll a dice
- Generate a password
- Tell me the current time

--- Step 1 ---
Planner Decision:
TASK: Roll a dice
TOOL: roll_dice
Observation: 2
completed

--- Step 2 ---
Planner Decision:
Based on the available tools and the pending tasks, I select the following:

TASK: Generate a password
TOOL: generate_password
Observation: C.D]Ex9hzwf2
completed

--- Step 3 ---
Planner Decision:
Based on the provided information, I select the next unfinished task and the best tool to complete it.

TASK: Tell me the current time
TOOL: current_time
Observation: 03-11-2026 19:02:10
completed

--- Step 4 ---
Planner Decision:
TASK: FINISH

Final Answer
------------
Here are the results:

You rolled a 2 on the dice.
Your generated password is C.D]Ex9hzwf2.
The current time is 03-11-2026 19:02:10.
(venv) 
```

#### `What time is it?` (1 task)
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

User : What time is it?

Task Plan
---------
- Check current system time
- Display current time to user

--- Step 1 ---
Planner Decision:
TASK: Check current system time
TOOL: current_time
Observation: 03-11-2026 19:06:17
completed

--- Step 2 ---
Planner Decision:
TASK: Display current time to user
TOOL: current_time
Observation: 03-11-2026 19:06:27
completed

--- Step 3 ---
Planner Decision:
TASK: FINISH

Final Answer
------------
The current time is 03-11-2026 19:06:27.
```

#### `Explain what an API is.` (no-tool task)
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

User : Explain what an API is

Task Plan
---------
- Define the term "API"
- Research existing definitions of API
- Create a list of key characteristics of an API
- Write a concise explanation of an API

--- Step 1 ---
Planner Decision:
TASK: Define the term "API"
TOOL: generate_password
Observation: ?i^*--1Yo}\[
completed

--- Step 2 ---
Planner Decision:
TASK: Research existing definitions of API
TOOL: roll_dice
Observation: 3
completed

--- Step 3 ---
Planner Decision:
TASK: Create a list of key characteristics of an API
TOOL: roll_dice
Observation: 6
completed

--- Step 4 ---
Planner Decision:
TASK: Write a concise explanation of an API
TOOL: none
Observation: No tool needed. Answer this task from general knowledge.
completed

--- Step 5 ---
Planner Decision:
TASK: FINISH

Final Answer
------------
An API, or Application Programming Interface, is a set of defined rules that enables different software systems to communicate with each other. It allows one system to request services or data from another system, and receive the response in a structured format. Think of it like a messenger between different systems, allowing them to work together seamlessly.
(venv)
```

**Observation:**
<!-- e.g. Plan had 3 tasks, each ticked off, the agent finished by itself, and the answer showed the exact password and time. -->

---

## 🔍 P1 → P2 and Day 9 → Day 10

| | Day 9 | Day 10 P1 | Day 10 P2 |
|---|---|---|---|
| Task plan | ❌ | ✅ | ✅ |
| Task status (☐ / ☑) | ❌ | ❌ | ✅ |
| Tools via MCP | ✅ | ❌ | ✅ |
| Planner output | tool | — | task + tool |
| Finish decided by | LLM | — | **Code** (+ LLM) |
| No-tool tasks | ❌ | listed | ✅ answered |
| Separate answer module | in `runner.py` | — | `answer.py` |

---

## ⚠️ Remaining Limitations / Next Improvements

1. **The task wording must match.** If the planner rephrases a task ("Get time" vs "Get the current time"), `complete_task()` doesn't tick it, and the same task repeats until `max_steps`. Better: let the planner answer with a **task number** (`TASK: 2`), or tick off the **current pending task** in code.
2. **No re-planning.** If a step fails permanently, the plan isn't changed. Advanced agents re-plan after failures.
3. **No dependencies or arguments.** Tasks can't use earlier results ("password with today's date"), and tools get no arguments ("20-character password" → still 12).
4. **Many LLM calls.** 3 tasks = 1 decompose + 3 planner + 1 answer = **5 LLM calls**. A simple tool task could skip the planner by mapping tasks to tools directly.
5. **The state grows into the prompt.** Raw Python lists and dicts are sent to the planner. For long tasks, summarise or format them as readable lines.
6. **`results` duplicates `observations`.** Both hold the tool outputs. `results` could be kept for notes only.
7. **The password and time go through the LLM** in the answer. The rules help, but printing exact values directly is safest (Day 7 lesson).
8. **The date is ambiguous:** `%d-%m-%Y` can be misread. Use `"%d %B %Y, %H:%M:%S"` (Day 7 lesson).
9. **One request per run.** Wrap the input + loop in `while True` with `quit` for a chat-style agent.

---

## 🛠️ Troubleshooting

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `ToolError: Unknown tool: none` (or another invented name) | Course `executor.py` has no handling for no-tool tasks or wrong names | Use the fixed `executor.py` above |
| Final answer is empty | `max_steps` reached (course `loop.py`) | Use the fixed `loop.py` (safety net) |
| Task Plan has lines like `<think>` or `1. Get time` | The model ignored the format | Fixed `task_planner.py` + use `llama3.2` |
| Same task repeats until max steps | The planner rephrased the task, so it's never ticked | Limitation #1; `temperature=0` + `llama3.2` reduce it |
| `Invalid planner decision.` | The reply had no `TASK:`/`TOOL:` lines | Small model; use `llama3.2` |
| `MCPError: Connection closed` | stdio on this PC | In-memory `mcp_client.py` (Day 8) |
| `ModuleNotFoundError: No module named 'state'` | Wrong folder | `cd Day10_P2` first |
| Traceback shows `...\Python310\...` | The venv isn't really active | `source venv/Scripts/activate` → check `which python` (Day 8) |

---

## ✅ Key Takeaways

- **Task decomposition** = break a big goal into small, ordered tasks **before** acting, like a to-do list.
- **Plan-and-Execute:** decompose → pick a pending task + tool → execute → tick it off → repeat → answer.
- Tracking **task status** (pending / completed) gives visible progress and a **reliable, code-decided finish**.
- Not every task needs a tool. A **"no tool"** path lets the LLM handle knowledge tasks.
- **Code should enforce what the LLM can't be trusted with:** finish checks, error handling, step limits.
- A plan is only as good as the decomposition. Next steps are **re-planning**, **dependencies** and **tool arguments**.

---

