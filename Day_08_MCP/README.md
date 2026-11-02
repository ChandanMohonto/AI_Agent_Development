# Day 08 — Model Context Protocol (MCP) 🔌🤖

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
| **Day 08** | **MCP — tools live in a server, and any AI can discover and use them** |

---

## 🎯 Goal of Day 8

Until Day 7, the tools lived **inside** our project (`tools.py`), and the planner prompt had the tool list **typed by hand**.

On Day 8 we move the tools into a separate **MCP server**. Our AI agent becomes an **MCP client** that:

1. 🔌 **connects** to the server
2. 🔍 **discovers** what tools exist, at runtime, with nothing hard-coded
3. 🧭 lets the LLM **plan** which tool to use
4. 🛠️ asks the server to **execute** it
5. 💬 turns the result into a **natural answer**

---

## 🤔 What Is MCP?

**MCP (Model Context Protocol)** is an **open standard** (introduced by Anthropic in late 2024) that defines **how AI applications connect to external tools and data**.

> 🔌 **Analogy: MCP is the "USB-C port" for AI.**
> Before USB, every device needed its own special cable. USB made one standard plug that works everywhere.
> Before MCP, every AI app needed its own custom code for every tool. MCP makes one standard: **build a tool server once, and any MCP-compatible AI can use it.**

### The problem MCP solves

```
WITHOUT MCP                              WITH MCP
───────────                              ────────
App A ──custom code──► Tool 1            App A ─┐
App A ──custom code──► Tool 2            App B ─┼──► MCP ──► Server 1 (tools)
App B ──custom code──► Tool 1            App C ─┘          └► Server 2 (tools)
App B ──custom code──► Tool 2
App C ──custom code──► ...               Each app speaks MCP once.
                                         Each server speaks MCP once.
N apps × M tools = N×M integrations      N + M integrations
```

### Why use MCP? (Benefits)

| Benefit | Explanation |
|---------|-------------|
| ♻️ **Build once, use everywhere** | The same `server.py` works with our agent, Claude Desktop, VS Code, Cursor and other MCP clients. |
| 🔍 **Dynamic tool discovery** | The client **asks** the server what tools exist. Add a tool to the server and every client sees it. **No client code change.** |
| 🧩 **Separation of concerns** | Tool code (server) and AI logic (client) live apart, and can be written by different people or teams. |
| 📏 **Standard format** | Tool names, descriptions and parameters always come in the same structure. |
| 🔒 **Control** | The server decides exactly which functions are exposed. The AI can't run anything else. |
| 🌍 **Local or remote** | The same server can run on your laptop or on the internet. |

### Limitations

| Limitation | Explanation |
|------------|-------------|
| 🧱 Extra layer | More moving parts than a simple `tools.py` import: a server, a client, a protocol. |
| ⏱️ Async code | MCP clients use `async`/`await`, which is new for many beginners. |
| 🔐 Security | A remote server exposes real actions, so it needs authentication and careful permissions. |
| 🤖 Still needs a planner | MCP tells the AI **what tools exist**. Choosing the right one is still the LLM's job (Day 7). |

---

## 🏗️ Major Components of MCP

```
┌─────────────────────────── HOST ─────────────────────────────┐
│  (the AI application: our agent.py, Claude Desktop, VS Code)  │
│                                                               │
│   ┌──────────┐      ┌───────────────┐                         │
│   │   LLM    │◄────►│  MCP CLIENT   │  (mcp_client.py)        │
│   │ (Ollama) │      │ connect/list/ │                         │
│   └──────────┘      │ call tools    │                         │
│                     └───────┬───────┘                         │
└─────────────────────────────┼─────────────────────────────────┘
                              │  TRANSPORT (stdio or HTTP)
                              │  messages in JSON-RPC 2.0
┌─────────────────────────────┼─────────────────────────────────┐
│                     ┌───────▼───────┐                         │
│                     │  MCP SERVER   │  (server.py)            │
│                     │               │                         │
│                     │  🛠️ Tools     │  current_time           │
│                     │  📄 Resources │  roll_dice              │
│                     │  💬 Prompts   │  generate_password      │
│                     └───────────────┘                         │
└───────────────────────────────────────────────────────────────┘
```

### 1. Roles

| Component | What it is | In our project |
|-----------|-----------|----------------|
| **Host** | The AI application the user talks to. It contains the LLM and one or more clients. | `agent.py` |
| **Client** | Lives inside the host. Keeps **one connection** to **one server**, and sends requests (list tools, call tool). | `mcp_client.py` (uses `fastmcp.Client`) |
| **Server** | A program that **exposes capabilities** (tools, data, prompts) in the MCP format. | `server.py` (uses `FastMCP`) |

### 2. What a server can offer (primitives)

| Primitive | Meaning | Analogy | Example |
|-----------|---------|---------|---------|
| 🛠️ **Tools** | Functions the AI can **call** to *do* something | Verbs | `roll_dice()`, `send_email()` |
| 📄 **Resources** | Data the AI can **read** | Nouns / files | a document, a database row, a config |
| 💬 **Prompts** | Reusable prompt templates | Recipes | "Summarize this bug report" |

> Day 8 uses **Tools** only. Resources and prompts work the same way, with `@mcp.resource()` and `@mcp.prompt()`.

### 3. Transport: how client and server talk

| Transport | How it works | Used for |
|-----------|-------------|----------|
| **stdio** | The client **starts the server as a child process** on the same computer and talks through standard input/output | Local tools; the standard for desktop apps like Claude Desktop |
| **HTTP** (Streamable HTTP) | The server runs as a **web service** at a URL; the client connects over the network | Remote / shared / hosted servers |
| **In-memory** (FastMCP) | The client is given the server **object** directly (`Client(mcp)`); both run in **one Python process** | Testing, and **what this project uses** (stdio failed on this Windows PC; see Troubleshooting) |

### 4. Messages: JSON-RPC 2.0

Every request and response is a small JSON message. You never write these by hand, because FastMCP does it, but this is what travels "on the wire":

```json
// client → server: "run roll_dice"
{"jsonrpc": "2.0", "id": 2, "method": "tools/call",
 "params": {"name": "roll_dice", "arguments": {}}}

// server → client: the result
{"jsonrpc": "2.0", "id": 2,
 "result": {"content": [{"type": "text", "text": "4"}]}}
```

### 5. Lifecycle of a session

```
1. initialize     client ⇄ server agree on protocol version & capabilities
2. tools/list     client: "what tools do you have?"  → names, descriptions, parameters
3. tools/call     client: "run roll_dice with {}"    → result
   ... (repeat 3 as many times as needed)
4. close          connection ends (server process stops for stdio)
```

---

## 🛠️ How to Develop an MCP Server (and Client)

We use **FastMCP**, a Python library that hides all the protocol details.

### Install

> ⚠️ **Version matters.** This course code is written for **FastMCP 2.x**. With the newest FastMCP (4.x, which installs `mcp` 2.x) the Python client fails at the handshake with `MCPError: Connection closed`. Pin `fastmcp<3`.
>
> ✅ **Tested with:** `fastmcp 2.14.7` + `mcp 1.30.0`, Python 3.10, Windows (Git Bash).

Add `fastmcp<3` to the root `requirements.txt`:

```
openai
python-dotenv
numpy
fastmcp<3
```

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pip show fastmcp mcp     # expect fastmcp 2.x and mcp 1.x, Location: ...\venv\...
```

### The recipe

**Server: 3 steps**

```python
from fastmcp import FastMCP

mcp = FastMCP("My Server")       # 1. create the server

@mcp.tool()                      # 2. turn any function into a tool
def add(a: int, b: int) -> int:
    """Add two numbers."""   #    ← docstring = description the AI reads
    return a + b

if __name__ == "__main__":
    mcp.run()                    # 3. start it (stdio by default)
```

**Client: 3 steps**

```python
from fastmcp import Client

async with Client("server.py") as client:          # 1. connect (stdio; or Client(mcp) for in-memory)
    tools  = await client.list_tools()             # 2. discover
    result = await client.call_tool("add", {"a": 2, "b": 3})   # 3. call
```

> 💡 Type hints (`a: int`) and docstrings are **not decoration**. FastMCP turns them into the tool's parameter schema and description, which is exactly what the LLM reads when choosing tools.

---

## 🌍 Where Is an MCP Server Hosted?

| Option | How | When to use |
|--------|-----|-------------|
| **1. Local (stdio)** | The client runs `python server.py` itself as a child process. Nothing is "hosted"; it lives on your PC. | Learning, personal tools, tools that use local files |
| **2. Local HTTP** | `mcp.run(transport="http", host="127.0.0.1", port=8000)` serves it at `http://127.0.0.1:8000/mcp` | Several apps on your PC sharing one running server |
| **3. Cloud / remote HTTP** | Deploy the HTTP version like any Python web app: a VPS, Docker, Render, Railway, Fly.io, AWS/GCP/Azure, or FastMCP's own hosting (FastMCP Cloud) | A team, or the public, using your tools from anywhere |

**Switch our server to HTTP** by changing only the last lines of `server.py`:

```python
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

…and in `mcp_client.py`:

```python
client = Client("http://localhost:8000/mcp")    # instead of Client(mcp)
```

> 🔐 **Before putting a server on the internet:** add authentication, use HTTPS, and expose only safe tools. A public server that can run real actions is a security risk.
>
> ℹ️ FastMCP's commands and options change quickly between versions (this README uses **2.14.7**), so check the docs at **gofastmcp.com** before deploying.

---

## 🔌 How to Use Your MCP Server

### A. With our own agent (Day 8 code)

```bash
cd Day_08_MCP/Day08_P4
python agent.py
```

### B. Test it visually with the MCP Inspector

A web UI that lists your tools and lets you click to run them, with no AI needed. It's great for QA.

```bash
cd Day_08_MCP/Day08_P1
fastmcp dev server.py
```

*(This is the FastMCP **2.x** command. In FastMCP 4.x it became `fastmcp dev inspector server.py`.)*

It opens a browser page. Click **Connect** → **Tools** → **List Tools** → pick `roll_dice` → **Run Tool**.

*(Node.js is required. Alternative: `npx @modelcontextprotocol/inspector python server.py`.)*

### C. With Claude Desktop (or any MCP-compatible app)

The **same `server.py`**, with no changes, can give its tools to Claude Desktop.

**Option 1: automatic**

```bash
fastmcp install claude-desktop server.py
```

**Option 2: manual.** Edit Claude Desktop's config file (Settings → Developer → Edit Config), `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "day8-tools": {
      "command": "D:\\AI Agents\\AI_Agent_Journy\\venv\\Scripts\\python.exe",
      "args": ["D:\\AI Agents\\AI_Agent_Journy\\Day_08_MCP\\Day08_P1\\server.py"]
    }
  }
}
```

| Field | Meaning |
|-------|---------|
| `"day8-tools"` | Any name you like for the server |
| `"command"` | The **venv** Python, because it has `fastmcp` installed |
| `"args"` | The **full path** to `server.py` |

Restart Claude Desktop, then ask *"Roll a dice for me"*. Claude will discover and call **your** `roll_dice` tool.

Other MCP clients (VS Code with Copilot, Cursor, Windsurf, …) use a very similar `command` + `args` config.

> This is the real power of MCP: **one server, many AI apps.**

---

## 🧩 The 4 Parts at a Glance

| Part | Course lessons | What we build | Key new code |
|------|----------------|---------------|--------------|
| **P1** | 98–103 | **MCP server** with 3 tools + **MCP client** + test | `server.py`, `mcp_client.py`, `test_client.py` |
| **P2** | 104–105 | **Agent skeleton**: connect and discover tools | `agent.py` |
| **P3** | 106–107 | **Planner** built from the **discovered** tool descriptions | `agent.py` (+ `planner()`) |
| **P4** | 108–110 | **Complete MCP-powered agent**: plan → execute via MCP → respond | `agent.py` (+ `generate_response()`) |

`server.py`, `mcp_client.py` and `test_client.py` are **identical in all 4 parts**. Only `agent.py` grows.

---

## 📁 Folder Structure

```
Day_08_MCP/
├── README.md
├── Day08_P1/
│   ├── server.py          # MCP server: 3 tools
│   ├── mcp_client.py      # helper functions: connect / discover / execute
│   └── test_client.py     # test the client ↔ server, no AI
├── Day08_P2/
│   ├── server.py
│   ├── mcp_client.py
│   ├── test_client.py
│   └── agent.py           # connect + discover
├── Day08_P3/
│   ├── ...                # same 3 files
│   └── agent.py           # + planner
└── Day08_P4/
    ├── ...                # same 3 files
    └── agent.py           # + execute + natural answer
```

## 📄 All Files — Brief Overview

| File | Role in MCP | One-line summary |
|------|-------------|------------------|
| `server.py` | **Server** | Creates a FastMCP server and exposes `current_time`, `roll_dice`, `generate_password` as tools. |
| `mcp_client.py` | **Client** | Four reusable async helpers: `connect()`, `disconnect()`, `discover_tools()`, `execute_tool()`. |
| `test_client.py` | Test | Connects, lists tools and calls `roll_dice`, proving the client and server work **without any AI**. |
| `agent.py` (P2) | **Host** | Connects and prints the discovered tools. |
| `agent.py` (P3) | Host + planner | Builds the planner prompt **from the server's tool descriptions**; the LLM picks a tool. |
| `agent.py` (P4) | Full agent | Plan → call the tool through MCP → the LLM writes a friendly answer. |

---

## ▶️ How to Run — Which File First?

> 🔑 **You do NOT run `server.py` yourself.** `mcp_client.py` imports the server and connects to it automatically. Running `python server.py` alone just starts it and waits for a stdio client (press `Ctrl + C`). That's only useful as a quick "does it start?" check.
>
> 🌐 **No browser is needed**, except for the optional MCP Inspector.
>
> ⚠️ Run from **inside each part folder**, because `from server import mcp` looks for `server.py` in the current folder.

### One-time setup

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
python -m pip install -r requirements.txt     # requirements.txt contains fastmcp<3
python -m pip show fastmcp mcp                # fastmcp 2.x, mcp 1.x, Location: ...\venv\...
```

**Check that the venv works inside the Day folder too:**

```bash
cd Day_08_MCP/Day08_P1
which python
```

✅ `/d/AI Agents/AI_Agent_Journy/venv/Scripts/python`
❌ `/c/Users/<you>/AppData/Local/Programs/Python/Python310/python`: the venv isn't really active. See **Troubleshooting → venv**.

### Run order

| # | Folder | Command | What it does | Expected |
|---|--------|---------|--------------|----------|
| 1 | `Day08_P1` | `python test_client.py` | Client connects to the server, lists tools, rolls a dice | 3 tool names + `Dice Result: <1–6>` ✅ confirmed |
| 2 | `Day08_P1` | `fastmcp dev server.py` *(optional)* | MCP Inspector in the browser, to click-test tools | Green "Connected" → Tools → List Tools → Run Tool. Stop with `Ctrl + C` |
| 3 | `Day08_P2` | `python agent.py` | Agent connects and discovers tools | `Connected to MCP Server.` + 3 tool names |
| 4 | `Day08_P3` | `python agent.py` | Type a request; the planner picks a tool | `Planner Selected: roll_dice` |
| 5 | `Day08_P4` | `python agent.py` | Full agent: plan → run tool via MCP → natural answer | e.g. *"You rolled a 4!"* |

```bash
cd "/d/AI Agents/AI_Agent_Journy/Day_08_MCP/Day08_P1"
python test_client.py

cd ../Day08_P2 && python agent.py
cd ../Day08_P3 && python agent.py
cd ../Day08_P4 && python agent.py
```

Confirmed output of step 1 (the `AuthlibDeprecationWarning` above it is harmless):

```
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

Dice Result: 2
```

> **Model tip:** your `.env` here used `qwen3:1.7b`. Small "thinking" models may return `<think>...</think>` or extra words instead of only a tool name, which makes the tool call fail. `llama3.2` is more reliable for planning (see limitations).

---

# Part 1 — MCP Server & MCP Client 🖥️⇄🔌

**Goal:** build a server that exposes tools, a client that can talk to it, and a test that proves they work, all **before** adding any AI.

## `server.py`: the MCP Server

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

### Step-by-step explanation

| Code | Meaning |
|------|---------|
| `from fastmcp import FastMCP` | Import the server class. |
| `mcp = FastMCP("Time Server")` | Create a server and give it a name (shown to clients). |
| `@mcp.tool()` | A **decorator**: registers the function below as an MCP tool. Without it, the function is invisible to clients. |
| `def current_time():` | The tool's **name** is the function name. |
| `"""Return the current date and time."""` | The tool's **description**. Clients (and the LLM planner) read this. |
| `return datetime.now().strftime("%d-%m-%Y %H:%M:%S")` | Day 4 tool logic, now in 24-hour format. |
| `roll_dice()` | `random.randint(1, 6)`, same as Day 4. |
| `generate_password(length: int = 12)` | The type hint `int` and default `12` become the tool's **parameter schema**: clients know it accepts an optional integer `length`. |
| `"".join(secrets.choice(alphabet) for _ in range(length))` | A shorter way to build the password than Day 4's loop. Same result, using a *generator expression*. |
| `import sys` + `print(..., file=sys.stderr)` | Log messages go to **stderr**. With stdio, **stdout is the MCP channel** and may carry only JSON messages. A normal `print()` breaks the connection (see Troubleshooting). |
| `if __name__ == "__main__": mcp.run()` | Start the server when the file is run. The default transport is **stdio**. |

**Compare with Day 4 `tools.py`:** the functions are almost the same. The only real change is the `@mcp.tool()` decorator. That one line makes them usable by **any** MCP client.

## `mcp_client.py`: the MCP Client helpers

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

    await client.__aexit__(None, None, None)


async def discover_tools(client):

    """
    Retrieve all tools from the server.
    """

    return await client.list_tools()


async def execute_tool(client, tool_name, arguments=None):

    """
    Execute a tool.
    """

    if arguments is None:
        arguments = {}

    return await client.call_tool(tool_name, arguments)
```

### In-memory vs stdio: which `connect()` to use

| Mode | Code | How it works | Status on this project |
|------|------|--------------|------------------------|
| **In-memory** ✅ | `from server import mcp` → `Client(mcp)` | Imports the server object and talks to it **inside the same Python process** | **Works.** Used in this README |
| **stdio** | `Client("server.py")` | Starts `server.py` as a **separate process** and talks through stdin/stdout | Failed with `Connection closed` on this Windows + Git Bash PC (see Troubleshooting #5) |

Both use the **real MCP protocol**: the same `initialize` → `tools/list` → `tools/call` messages, the same tools and the same results. Only the "cable" between client and server differs. `server.py` needs **no change** for either mode.

> 💡 On another PC (or in Command Prompt / macOS / Linux), stdio may work fine. To try it, replace the two lines in `connect()` with `client = Client("server.py")` and remove `from server import mcp`.

### Step-by-step explanation

**What is `async` / `await`?** Talking to a server means **waiting** (for it to start, for replies). `async def` creates a function that can wait without freezing the program, and `await` marks the waiting points. Async functions must be run with `asyncio.run(...)`.

| Function | Code | Meaning |
|----------|------|---------|
| `from server import mcp` | | Import the **server object** created in `server.py`. Importing doesn't run `mcp.run()`, because that's inside `if __name__ == "__main__":`. |
| `connect()` | `Client(mcp)` | Create a client connected **in-memory** to that server object. |
| | `await client.__aenter__()` | Opens the connection and does the MCP `initialize` handshake. (This is what `async with` does internally.) |
| | `return client` | Hand back the connected client for later calls. |
| `disconnect(client)` | `await client.__aexit__(None, None, None)` | Closes the connection. The three `None`s mean "no error happened". |
| `discover_tools(client)` | `await client.list_tools()` | Sends `tools/list` and returns tool objects, each with `.name`, `.description` and `.inputSchema`. |
| `execute_tool(client, tool_name, arguments=None)` | `if arguments is None: arguments = {}` | Safe default: no arguments means an empty dict. (Never use `={}` as a default; mutable defaults are a classic Python bug.) |
| | `await client.call_tool(tool_name, arguments)` | Sends `tools/call` and returns a **result object**. The text is in `result.content[0].text`. |

## `test_client.py`: test client ↔ server, no AI

```python
import asyncio

from mcp_client import *

async def main():

    client = await connect()

    tools = await discover_tools(
        client
    )

    print()

    print("Available Tools")

    print("----------------")

    for tool in tools:

        print(tool.name)

    print()

    result = await execute_tool(

        client,

        "roll_dice"

    )

    print("Dice Result:", result.content[0].text)

    await disconnect(
        client
    )


asyncio.run(main())
```

| Code | Meaning |
|------|---------|
| `from mcp_client import *` | Import all helper functions. |
| `client = await connect()` | Connect to the server. |
| `tools = await discover_tools(client)` | Ask what tools exist. |
| `for tool in tools: print(tool.name)` | Print each tool's name. |
| `execute_tool(client, "roll_dice")` | Run a tool **by name** through MCP. |
| `result.content[0].text` | MCP results are a list of content blocks; the first block's text is the dice number. |
| `await disconnect(client)` | Close cleanly. |
| `asyncio.run(main())` | Run the async `main()` function. |

### 📤 Output — Part 1

#### `python test_client.py`
```
$ python test_client.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

Dice Result: 2
(venv)
```

#### MCP Inspector — `fastmcp dev server.py` (optional, screenshot or notes)
```
 fastmcp dev server.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Starting MCP inspector...

MCP Inspector Web is up and running at:
   http://127.0.0.1:6274?MCP_INSPECTOR_API_TOKEN=810e84d8fc31525dd29e6b5045748d5153d8825a558136f3bdefad87dc45406b

   Sandbox (MCP Apps): http://127.0.0.1:6275/sandbox

   Auth token: 810e84d8fc31525dd29e6b5045748d5153d8825a558136f3bdefad87dc45406b

   Secrets: OS keychain

Opening browser...
```

**Observation:**
<!-- e.g. The client discovered all 3 tools without any tool list in the client code. -->

---

# Part 2 — Agent Skeleton: Connect & Discover 🔍

**Goal:** start the AI agent (the **host**) with the first two steps: connect to the server and discover its tools.

## `agent.py` (P2)

```python
import asyncio

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

from mcp_client import (
    connect,
    disconnect,
    discover_tools,
    execute_tool
)



async def main():
# Step 1: Connect to the MCP Server.
    client = await connect()

    # Step 2: Discover all available tools.
    tools = await discover_tools(
        client
    )
    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)
    print() 

    
    await disconnect(
        client
    )

if __name__ == "__main__":

    asyncio.run(main())
```

### Step-by-step explanation

| Code | Meaning |
|------|---------|
| `load_dotenv()` + `OpenAI(...)` | The LLM client (Ollama), prepared for the next parts. Not used yet. |
| `from mcp_client import (...)` | The MCP helpers from P1. |
| `async def main():` | The agent's main flow, async because MCP calls are async. |
| `client = await connect()` | **Step 1**: connect to the MCP server. |
| `tools = await discover_tools(client)` | **Step 2**: discover tools. |
| loop + `print(tool.name)` | Show what the agent can do. |
| `await disconnect(client)` | Close. |
| `if __name__ == "__main__": asyncio.run(main())` | Run only when executed directly. |

> 💡 Notice that `agent.py` has **no `import tools`** and **no tool names written anywhere**. Everything it knows about tools comes from the server.

> ⚠️ **Name clash:** `client` at the top is the **OpenAI (LLM) client**, but inside `main()` a new `client` is the **MCP client**. They're different objects with the same name. It works, because inside `main()` the local one wins, but `llm` and `mcp_client` would be clearer names.

### 📤 Output — Part 2

#### `python agent.py`
```
python agent.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

(venv) 
```

**Observation:**

---

# Part 3 — Planner from Discovered Tools 🧭

**Goal:** let the LLM choose a tool, using descriptions **fetched from the MCP server** instead of a list typed into the prompt (as on Day 7).

## `agent.py` (P3)

```python
import asyncio

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

from mcp_client import (
    connect,
    disconnect,
    discover_tools,
    execute_tool
)

# Build Tool Descriptions
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


def planner(user_request, tools):

    tool_descriptions = build_tool_descriptions(
        tools
    )

    ###Then create a prompt by combining user input and Tool Description.  and Give this prompt to Ollama. ###

    prompt = f"""
You are an AI Planner.

Available Tools

{tool_descriptions}

Instructions

1. Select the best tool.
2. Reply ONLY with the tool name.
3. Do not explain.

User Request

{user_request}
"""
# Give this prompt to ollama
    response = client.chat.completions.create (

        model= os.getenv("MODEL"),

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

#Ollama returns the tool name
    tool_name = response.choices[0].message.content

    return tool_name.strip()


async def main():
# Step 1: Connect to the MCP Server.
    client = await connect()

    # Step 2: Discover all available tools.
    tools = await discover_tools(
        client
    )
    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)
    print() 

    ### Step 3: Planner: Take the User Input (Question). Create Tool Descriptions for each tool. Then create a prompt by combining user input and Tool Description.  and Give this prompt to Ollama. ###

    user_request = input(
        "User : "
    )

    tool_name = planner(
        user_request,
        tools
    )

    print()

    print(
        "Planner Selected:",
        tool_name
    )


    await disconnect(
        client
    )

if __name__ == "__main__":

    asyncio.run(main())
```

### Step-by-step explanation

**1. `build_tool_descriptions(tools)`**

```python
for tool in tools:
    descriptions += f"""
Tool:
{tool.name}

Description:
{tool.description}
----------------------------
"""
```

This turns the server's tool list into text for the prompt:

```
Tool:
current_time

Description:
Return the current date and time.
----------------------------
Tool:
roll_dice

Description:
Roll a six-sided dice.
----------------------------
...
```

The descriptions are the **docstrings** from `server.py`, delivered through MCP.

**2. `planner(user_request, tools)`**

| Prompt part | Purpose |
|-------------|---------|
| `You are an AI Planner.` | Role. |
| `Available Tools` + `{tool_descriptions}` | The **dynamic** menu from the server. |
| `1. Select the best tool.` `2. Reply ONLY with the tool name.` `3. Do not explain.` | A strict output format, so Python can use the reply directly. |
| `User Request {user_request}` | The user's question. |

`response.choices[0].message.content.strip()` → the tool name, e.g. `roll_dice`.

**3. `main()`**: connect → discover → `input("User : ")` → `planner(...)` → print `Planner Selected: roll_dice` → disconnect.

### Day 7 vs Day 8 planner

| | Day 7 | Day 8 |
|---|---|---|
| Tool list in the prompt | Typed by hand | **Generated from the MCP server** |
| Add a new tool | Edit `tools.py` + the planner prompt + the `if/elif` | Add one `@mcp.tool()` function in `server.py`. **Done.** |
| Where tools run | Same Python process | MCP server (separate process) |

### 📤 Output — Part 3

#### `What time is it?`
```
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : What time is it?

Planner Selected: current_time
(venv) 
```

#### `Roll a dice`
```
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : Roll a dice

Planner Selected: roll_dice
(venv)
```

#### `Give me a secure password`
```
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : Give me a secure password

Planner Selected: generate_password
(venv) 
```

**Observation:**

---

# Part 4 — The Complete MCP-Powered AI Agent 🤖

**Goal:** finish the loop: **plan → execute through MCP → answer naturally**.

## `agent.py` (P4)

```python
import asyncio

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

from mcp_client import (
    connect,
    disconnect,
    discover_tools,
    execute_tool
)

# Build Tool Descriptions
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


def planner(user_request, tools):

    tool_descriptions = build_tool_descriptions(
        tools
    )

    ###Then create a prompt by combining user input and Tool Description.  and Give this prompt to Ollama. ###

    prompt = f"""
You are an AI Planner.

Available Tools

{tool_descriptions}

Instructions

1. Select the best tool.
2. Reply ONLY with the tool name.
3. Do not explain.

User Request

{user_request}
"""
# Give this prompt to ollama
    response = client.chat.completions.create (

        model= os.getenv("MODEL"),

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

#Ollama returns the tool name
    tool_name = response.choices[0].message.content

    return tool_name.strip()

def generate_response(user_request, tool_result):

    prompt = f"""
The user asked:

{user_request}

The tool returned:

{tool_result}

Respond directly to the user in a natural, conversational way.

Use the tool result as the factual source.
Transform raw tool output into a human-friendly answer.
Do not simply copy raw values when a natural sentence would be better.
Do not add information that is not needed to answer the request.
Do not mention tools, internal processing, planning, or reasoning.
Keep the response concise.
"""

    response = client.chat.completions.create (

        model=os.getenv("MODEL"),

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

    return response.choices[0].message.content



async def main():
# Step 1: Connect to the MCP Server.
    client = await connect()

    # Step 2: Discover all available tools.
    tools = await discover_tools(
        client
    )
    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)
    print() 

    ### Step 3: Planner: Take the User Input (Question). Create Tool Descriptions for each tool. Then create a prompt by combining user input and Tool Description.  and Give this prompt to Ollama. ###

    user_request = input(
        "User : "
    )

    tool_name = planner(
        user_request,
        tools
    )

    print()

    print(
        "Planner Selected:",
        tool_name
    )

# Step 5.    Execute the selected tool.
    tool_result = await execute_tool(client, tool_name)
# Step 6. Generate a natural language response.

    final_answer = generate_response(user_request, tool_result)

    print()

    print(final_answer)



    await disconnect(
        client
    )

if __name__ == "__main__":

    asyncio.run(main())
```

### Step-by-step explanation (new parts)

**1. `generate_response(user_request, tool_result)`**

| Prompt rule | Why |
|-------------|-----|
| `The user asked: ...` / `The tool returned: ...` | Gives the LLM the question **and** the real data. |
| `Use the tool result as the factual source.` | Grounding: don't guess (Days 5–7). |
| `Transform raw tool output into a human-friendly answer.` | `4` → *"You rolled a 4!"* |
| `Do not add information that is not needed…` | Stay short and on-topic. |
| `Do not mention tools, internal processing, planning, or reasoning.` | The user should see an answer, not the machinery. |
| `Keep the response concise.` | Short replies. |

**2. Steps 5 and 6 in `main()`**

```python
tool_result = await execute_tool(client, tool_name)      # Step 5: run it on the MCP server
final_answer = generate_response(user_request, tool_result)  # Step 6: natural answer
print(final_answer)
```

### The full flow

```
python agent.py
     │
     ▼
1. connect()                 → starts server.py (stdio), MCP handshake
2. discover_tools()          → [current_time, roll_dice, generate_password]
3. input("User : ")          → "Roll a dice for me"
4. planner()      (LLM #1)   → "roll_dice"
5. execute_tool() (MCP)      → server runs roll_dice() → 5
6. generate_response() (LLM #2) → "You rolled a 5! 🎲"
7. disconnect()              → server process stops
```

### 📤 Output — Part 4

#### `What time is it?`
```
----------------
current_time
roll_dice
generate_password

User : What time is it?

Planner Selected: current_time

It's currently 2:11 2026, 9:43 PM.
(venv) 
```

#### `Roll a dice for me`
```

Available Tools
----------------
current_time
roll_dice
generate_password

User : Roll a dice for me

Planner Selected: roll_dice

You rolled a three.
(venv) 
```

#### `I need a secure password`
```
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : I need a secure password

Planner Selected: generate_password

"Consider using a passphrase, a sequence of characters that's easy for you to remember, but hard for others to guess. Try making it at least 12 characters long and using a mix of uppercase and lowercase letters, numbers, and special characters, like 7*_dL6[x;. Make it unique and don't use easily guessable information like your birthdate or common words."
(venv)
```

#### A request no tool can answer — e.g. `Explain Python`
```
 python agent.py
D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\server\auth\providers\jwt.py:10: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, JsonWebToken
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : Explain Python

Planner Selected: There is no Python tool available.
Tool 'There is no Python tool available.' not listed, no validation will be performed
Traceback (most recent call last):
  File "D:\AI Agents\AI_Agent_Journy\Day_08_MCP\Day08_P4\agent.py", line 178, in <module>
    asyncio.run(main())
  File "C:\Users\chand\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "C:\Users\chand\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 649, in run_until_complete
    return future.result()
  File "D:\AI Agents\AI_Agent_Journy\Day_08_MCP\Day08_P4\agent.py", line 161, in main
    tool_result = await execute_tool(client, tool_name)
  File "D:\AI Agents\AI_Agent_Journy\Day_08_MCP\Day08_P4\mcp_client.py", line 48, in execute_tool
    return await client.call_tool(tool_name, arguments)
  File "D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\client\client.py", line 1430,in call_tool
    return await self._parse_call_tool_result(
  File "D:\AI Agents\AI_Agent_Journy\venv\lib\site-packages\fastmcp\client\client.py", line 1317,in _parse_call_tool_result
    raise ToolError(msg)
fastmcp.exceptions.ToolError: Unknown tool: There is no Python tool available.
(venv) 
```

**Observation:**
<!-- e.g. Time and dice worked; "Explain Python" … see limitations #1 -->

---

## 🔍 P1 → P4 Comparison

| | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| MCP server + tools | ✅ | ✅ | ✅ | ✅ |
| Client connects & discovers | ✅ (test) | ✅ | ✅ | ✅ |
| LLM involved | ❌ | ❌ | ✅ planner | ✅ planner + responder |
| Tool executed via MCP | ✅ (fixed: dice) | ❌ | ❌ | ✅ (chosen by the LLM) |
| Natural-language answer | ❌ | ❌ | ❌ | ✅ |

---

## ⚠️ Known Limitations / Improvements

1. **There's no `none` option.** The planner **must** pick a tool, so *"Explain Python"* is forced onto a tool, or returns text that isn't a tool name, and `call_tool` fails. Add *"If no tool fits, reply: none"* and, for `none`, answer with the LLM directly.
2. **No tool-name cleaning.** The reply goes straight into `call_tool()`. `Roll_dice`, `` `roll_dice` ``, `roll_dice.` or qwen3's `<think>...</think>` causes an **unknown tool error**. Reuse Day 7's `clean_tool_name()` and check the name exists in `[t.name for t in tools]`.
3. **No tool arguments.** `execute_tool(client, tool_name)` always sends `{}`, so "a 20-character password" still gives 12. The server already supports `length`, and its schema is in `tool.inputSchema`. Next step: ask the planner for JSON like `{"tool": "generate_password", "arguments": {"length": 20}}`.
4. **The raw result object is sent to the LLM.** `tool_result` is a `CallToolResult` object, so the prompt contains its long Python representation. Pass the text instead: `tool_result.content[0].text`.
5. **One question per run.** There's no `while True` loop, so the agent connects, answers once and exits. Wrap steps 3–6 in a loop with `quit` (connect once, ask many times).
6. **Disconnect isn't guaranteed.** If anything fails, `disconnect()` never runs. Use `try/finally`, or simply `async with Client(mcp) as client:`.
7. ~~**`print()` inside a stdio server.**~~ ✅ **Fixed in the code above.** The original `print("Starting MCP server..")` wrote to stdout, the MCP channel, and broke stdio connections. It now prints to `stderr`. Never use a plain `print()` in a stdio MCP server.
8. **The date is ambiguous.** `"%d-%m-%Y"` gives `02-11-2026`, which an LLM can read as February 11 (seen on Day 7). Use `"%d %B %Y, %H:%M:%S"` instead.
9. **The password goes through the LLM.** The responder may re-type it wrongly. Print exact values directly.
10. **The server name is misleading.** `FastMCP("Time Server")` also rolls dice and makes passwords, so `"Utility Tools"` would fit better.
11. **Must run from the part folder** because `from server import mcp` imports `server.py` from the current folder.
12. **stdio didn't work on this PC**, so the project uses in-memory mode. The agent and server run in one process, which is fine for learning. For a real separate server, use HTTP (see "Where Is an MCP Server Hosted?") or a PC where stdio works.
13. **The sync LLM call is inside async code.** `client.chat.completions.create` blocks the event loop. That's fine for one user; use `AsyncOpenAI` for concurrent agents.

---

## 🛠️ Troubleshooting: Problems We Faced & How We Solved Them

Day 8 took the longest to get running. Most problems were **environment** problems, not code. They're listed here in the order they happened, so anyone hitting the same errors can follow the same path.

### Timeline

| # | Problem | Real cause | Solution |
|---|---------|-----------|----------|
| 1 | `fastmcp dev server.py` → `Unknown command "server.py". Available commands: inspector, apps.` | The global Python had **FastMCP 4.1.5**, where the command changed | In a clean venv with `fastmcp<3`, `fastmcp dev server.py` is correct. (4.x: `fastmcp dev inspector server.py`) |
| 2 | `Failed to parse JSONRPC message` … `input_value='Starting MCP server..'` | `print()` in `server.py` wrote text to **stdout**, the MCP channel | `print("...", file=sys.stderr)` |
| 3 | `FastMCPDeprecationWarning: Inferring a stdio transport from the string 'server.py'…` | A FastMCP 4.x warning | Gone after switching to FastMCP 2.x |
| 4 | Prompt shows `(venv)`, but tracebacks show `C:\Users\<you>\...\Python310\...` and `which python` shows the global Python or a broken path like `/d/AI Agents/.../\AI Agents\...\venv/Scripts/python` | The Python 3.10 `activate` script writes a Windows path that **Git Bash mis-reads** (worse with the space in `AI Agents`). The venv was **never really used** | Fix `activate` with `sed` (below), re-activate in every new terminal, and always check `which python` |
| 5 | `MCPError: Connection closed` at `session.initialize()`, every time, even with the venv and FastMCP 2.14.7 | Starting `server.py` as a **separate stdio process** fails on this Windows + Git Bash setup. The server and library are fine (proved by the tests below) | Use **in-memory mode**: `Client(mcp)` in `mcp_client.py` ✅ |
| 6 | `WARNING: Ignoring invalid distribution -ip` | A broken leftover folder from an interrupted pip install in the **global** Python | Harmless; using the venv avoids it |
| 7 | `AuthlibDeprecationWarning: authlib.jose module is deprecated` | A warning from a FastMCP dependency | Harmless; ignore it |
| 8 | Server banner says `Update available: 4.1.5` / `FastMCP 3.0 is coming` | Just a notice | **Don't upgrade**; this code needs `fastmcp<3` |

### Fix: venv activation in Git Bash (problem 4)

From the project root:

```bash
cd "/d/AI Agents/AI_Agent_Journy"
deactivate                     # ignore "command not found"
sed -i 's|^VIRTUAL_ENV=.*|VIRTUAL_ENV="/d/AI Agents/AI_Agent_Journy/venv"|' venv/Scripts/activate
source venv/Scripts/activate
which python                   # /d/AI Agents/AI_Agent_Journy/venv/Scripts/python
```

- **Don't trust the `(venv)` label.** A new VS Code terminal can show it without really using the venv. Check `which python` in **each new terminal**, and in the Day folder too.
- **Guaranteed alternative:** call the venv Python by its full path:
  ```bash
  "/d/AI Agents/AI_Agent_Journy/venv/Scripts/python" test_client.py
  ```
- If you recreate the venv, run the `sed` line again.

### Fix: clean venv with the right FastMCP version (problems 1, 3)

```bash
cd "/d/AI Agents/AI_Agent_Journy"
rm -rf venv
python -m venv venv
sed -i 's|^VIRTUAL_ENV=.*|VIRTUAL_ENV="/d/AI Agents/AI_Agent_Journy/venv"|' venv/Scripts/activate
source venv/Scripts/activate
python -m pip install -r requirements.txt     # contains fastmcp<3
python -m pip show fastmcp mcp                # fastmcp 2.14.7, mcp 1.30.0, Location: ...\venv\...
```

### How we found the real cause of `Connection closed` (problem 5)

Guessing didn't work: changing how the server starts, turning off the banner, and changing the encoding all failed. What worked was **isolating each piece with small tests**, the same way you'd narrow down a bug in QA.

| Test | Command (in `Day08_P1`) | Result | What it proved |
|------|-------------------------|--------|----------------|
| MCP Inspector | `fastmcp dev server.py` | ✅ Connected | The server code is valid (with a Node.js client) |
| 1. Server alone | `"/d/.../venv/Scripts/python" server.py` | ✅ Starts and waits | The server doesn't crash on start-up with the venv Python |
| 2. In-memory client | `python test_inmemory.py` (`Client(mcp)`) | ✅ 3 tools + dice result | The tools, FastMCP and the Python client all work |
| stdio client | `python test_client.py` (`Client("server.py")`) | ❌ Connection closed | **Only** the separate-process (stdio) connection fails |

**Conclusion:** everything works except starting the server as a subprocess from Git Bash on this PC, so the project uses **in-memory mode**.

`test_inmemory.py`, the test that proved it:

```python
import asyncio
from fastmcp import Client
from server import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print([tool.name for tool in tools])

        result = await client.call_tool("roll_dice", {})
        print("Dice Result:", result.content[0].text)


asyncio.run(main())
```

> 🧪 Want to try stdio again later? Run `test_client.py` with `Client("server.py")` from a real **Command Prompt** (`D:\...>`, not Git Bash `$`), or on another PC. Git Bash isn't a true Windows console and can break subprocess pipes.

### Small mistakes worth knowing

| Mistake | What happened | Tip |
|---------|---------------|-----|
| `cd Day08_P1` while already inside `Day08_P1` | `No such file or directory` | Check the folder in your prompt, or use full paths: `cd "/d/AI Agents/AI_Agent_Journy/Day_08_MCP/Day08_P1"` |
| `python test_client.py` from `Day_08_MCP` | `can't open file ...\Day_08_MCP\test_client.py` | Run inside the **part** folder (`Day08_P1`, …) |
| Files created with `touch` | Empty files → `ImportError: cannot import name ...` | Paste the code in, then check with `find . -type f -empty` |

### Apply the fix to all 4 parts

`server.py` and `mcp_client.py` are identical in P1–P4:

```bash
cd "/d/AI Agents/AI_Agent_Journy/Day_08_MCP"
for p in 2 3 4; do cp Day08_P1/server.py Day08_P1/mcp_client.py Day08_P$p/; done
```

---

## ✅ Key Takeaways

- **MCP is a standard plug** between AI apps and tools: build a tool server once, and any MCP client can use it.
- **Host** (the AI app) → **Client** (the connection) → **Server** (the tools, resources and prompts).
- Transports: **stdio** for local (the client starts the server), **HTTP** for remote or hosted.
- FastMCP: `@mcp.tool()` + a docstring + type hints, and the function becomes a discoverable tool.
- The client flow is always **connect → list_tools → call_tool → disconnect**.
- **Dynamic discovery** means the planner prompt is built from the server, so adding a tool requires **no agent code change**.
- The same `server.py` works with **our agent, MCP Inspector and Claude Desktop**.
- **Pin library versions** (`fastmcp<3`) and **check `which python`**, because most "mysterious" errors were environment problems, not code.
- When something fails, **isolate it with small tests** (server alone → in-memory → stdio) instead of guessing.
- **In-memory mode** (`Client(mcp)`) uses the same MCP protocol without a separate process, which is perfect for testing and for PCs where stdio fails.

---

