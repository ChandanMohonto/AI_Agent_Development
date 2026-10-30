# Simple AI Assistant Chatbot with Ollama

A beginner-friendly chatbot that runs **locally** with [Ollama](https://ollama.com), uses the **OpenAI Python library** to talk to it, and has a small **HTML page** where you type a question and get the answer through an API.

```
Browser (index.html)  --->  Flask API (/ask)  --->  Ollama (local LLM)
      question                  server.py              llama3.2
      <---  answer  <-----------------  <-------------
```

---

## 1. Prerequisites

| Requirement | Why |
|---|---|
| Python 3.9+ | To run the code |
| Ollama installed | Runs the AI model on your own computer |
| A model pulled | The "brain" of the chatbot |

Install Ollama from https://ollama.com, then pull a model and make sure it runs:

```bash
ollama pull llama3.2
ollama run llama3.2      # type /bye to exit
```

Ollama automatically serves an OpenAI-compatible API at `http://localhost:11434/v1`.

### Windows: install and fix common errors

**Which terminal am I in?**

| Prompt looks like | Terminal | Notes |
|---|---|---|
| `C:\WINDOWS\system32>` | Command Prompt (CMD) | `irm` does **not** work here |
| `PS D:\...>` | PowerShell | `irm` works here |
| `chand@PC MINGW64 /d/...$` | Git Bash | `irm` does **not** work here |

> `irm https://ollama.com/install.ps1 | iex` is a **PowerShell-only** command. In CMD or Git Bash you get `irm: command not found`.

**Easiest install:** download `OllamaSetup.exe` from https://ollama.com/download and run it. Wait until the Ollama icon appears in the system tray.

**Check the install (PowerShell):**

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

**Pull the model and confirm it:**

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama3.2
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
```

`ollama list` should show `llama3.2:latest`.

**Fix: `ollama: command not found` / `'ollama' is not recognized`**

The install worked, but the terminal can't find it on PATH.

- **PowerShell / CMD (permanent fix):** run in PowerShell, then **close all terminals** and open a new one.

  ```powershell
  $p = "$env:LOCALAPPDATA\Programs\Ollama"
  [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$p", "User")
  ```

- **Git Bash (permanent fix):** run once (replace `chand` with your Windows username).

  ```bash
  echo 'export PATH="$PATH:/c/Users/chand/AppData/Local/Programs/Ollama"' >> ~/.bashrc
  source ~/.bashrc
  ollama --version
  ```

**Check the Ollama service is running:**

```bash
curl http://localhost:11434
```

Expected output: `Ollama is running`. If not, open the Ollama app from the Start menu.

> Your chatbot code only talks to `http://localhost:11434`. It does **not** need the `ollama` command on PATH, only the running service.

---

## 2. Project Setup

### Step 1: Create the project folder and virtual environment

```bash
mkdir ollama-chatbot
cd ollama-chatbot
python -m venv venv
```

### Step 2: Activate the virtual environment

Pick the command that matches your terminal:

```powershell
# Windows PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
venv\Scripts\Activate.ps1
```

```bash
# Windows Git Bash
source venv/Scripts/activate

# Windows CMD
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

> The `Set-ExecutionPolicy -Scope Process` line only affects the current PowerShell window. It fixes the "running scripts is disabled" error without changing your system settings.

### Step 3: Install the packages

```bash
pip install openai python-dotenv flask
```

| Package | Purpose |
|---|---|
| `openai` | Client library to call the Ollama API (OpenAI-compatible) |
| `python-dotenv` | Loads settings from the `.env` file |
| `flask` | Creates the small web API for the HTML page |

> **Let the install finish.** Pressing Ctrl+C during `pip install` shows `ERROR: Operation cancelled by user` and leaves packages **half-installed**. If that happens, run the command again and wait until you see `Successfully installed ...`.

Verify everything installed:

```bash
pip list
```

You should see `openai`, `python-dotenv` and `flask` in the list.

Optional: remove the "new release of pip" notice with `python -m pip install --upgrade pip`.

### Step 4: Create the `day1` folder

```bash
mkdir day1
cd day1
```

> **Already inside a folder like `D:\AI Agents\Day_01`?** Skip this step and put `.env`, `chat.py`, `server.py` and `index.html` directly in that folder. Run all commands from there.

Final structure:

```
ollama-chatbot/
├── venv/
└── day1/
    ├── .env
    ├── chat.py
    ├── server.py
    └── index.html
```

---

## 3. The `.env` File

Create `day1/.env`:

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

- **BASE_URL**: where Ollama is listening.
- **API_KEY**: Ollama does not check it, but the OpenAI library requires some value, so `ollama` is used.
- **MODEL**: the model name you pulled (check with `ollama list`).

> Keep secrets out of your code. If you use Git, add `.env` to `.gitignore`.

---

## 4. Basic Chat in Python (`chat.py`)

Create `day1/chat.py`:

```python
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
```

Run it:

```bash
python chat.py
```

### What each part does

| Part | Explanation |
|---|---|
| `load_dotenv()` | Reads `.env` and puts values into environment variables |
| `import os` / `os.getenv("X")` | Reads those environment variables in Python |
| `OpenAI(base_url, api_key)` | Creates the client that sends requests to Ollama |
| `model` | Which model should answer |
| `messages` | The conversation. `system` sets behavior, `user` is your question |
| `temperature` | Creativity: 0 = focused and predictable, 1 = more creative |
| `max_tokens` | Maximum length of the answer |
| `response.choices[0].message.content` | The actual answer text |

---

## 5. The API (`server.py`)

This makes the same chat logic available to the HTML page through a URL.

Create `day1/server.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return jsonify({"answer": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
```

How it works:

- `GET /` serves the HTML page.
- `POST /ask` receives `{"question": "..."}` and returns `{"answer": "..."}`.
- Serving the HTML from Flask itself avoids browser CORS problems.

---

## 6. The HTML Page (`index.html`)

Create `day1/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ollama Chatbot</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 16px; }
    textarea { width: 100%; height: 90px; padding: 8px; font-size: 16px; }
    button { margin-top: 8px; padding: 10px 20px; font-size: 16px; cursor: pointer; }
    #answer { margin-top: 20px; padding: 12px; background: #f3f3f3; border-radius: 6px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h2>AI Assistant (Ollama)</h2>
  <textarea id="question" placeholder="Ask me anything..."></textarea>
  <br />
  <button onclick="ask()">Ask</button>
  <div id="answer"></div>

  <script>
    async function ask() {
      const question = document.getElementById("question").value;
      const box = document.getElementById("answer");
      box.textContent = "Thinking...";

      try {
        const res = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });
        const data = await res.json();
        box.textContent = data.answer || data.error;
      } catch (err) {
        box.textContent = "Error: " + err.message;
      }
    }
  </script>
</body>
</html>
```

---

## 7. Run Everything

Make sure Ollama is running, your venv is active, and you are inside `day1`:

```bash
python server.py
```

Open **http://localhost:5000** in your browser, type a question, and click **Ask**.

You can also test the API directly:

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Kubernetes?"}'
```

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `irm: command not found` / `'irm' is not recognized` | `irm` is PowerShell-only. Open PowerShell, or use the `OllamaSetup.exe` installer |
| `ollama: command not found` / `'ollama' is not recognized` | Add Ollama to PATH (see Section 1), then open a **new** terminal |
| `running scripts is disabled` when activating venv | In PowerShell run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then activate again |
| `ERROR: Operation cancelled by user` during `pip install` | Install was interrupted. Re-run `pip install openai python-dotenv flask` and let it finish |
| `Connection error` | Ollama is not running. Start it with `ollama serve` or open the Ollama app |
| `model not found` | Run `ollama list` and make sure `MODEL` in `.env` matches exactly |
| `ModuleNotFoundError` | Virtual environment is not active, or run `pip install openai python-dotenv flask` |
| `.env` values are `None` | Run the script from inside the `day1` folder, and check the file is named exactly `.env` |
| Port 5000 already in use | Change `port=5000` in `server.py` to another port like `5001` |
| Slow answers | Use a smaller model like `llama3.2:1b` |

---

## 9. What Is Compulsory and Why

| Item | Compulsory? | Why |
|---|---|---|
| Ollama + a pulled model | Yes | It is the AI itself. Without it there is nothing to answer |
| Virtual environment (`venv`) | Recommended | Keeps packages isolated. The code runs without it, but it avoids version conflicts |
| `openai` package | Yes | Provides the client that talks to Ollama |
| `.env` file | Recommended | Keeps URL, key and model out of the code. You could hard-code them, but it is bad practice |
| `BASE_URL` | Yes | Tells the client to use Ollama instead of OpenAI's servers |
| `API_KEY` | Yes (any value) | The library refuses to start without one. Ollama ignores the value |
| `MODEL` | Yes | Tells Ollama which model should answer |
| `python-dotenv` (`load_dotenv`) | Only if using `.env` | Reads the `.env` file |
| `import os` | Only if using `.env` | Reads the loaded values with `os.getenv` |
| `OpenAI(...)` client | Yes | The object used to send requests |
| `messages` argument | Yes | The question or conversation sent to the model |
| `temperature`, `max_tokens` | Optional | Fine-tune creativity and answer length. Defaults work |
| `system` message | Optional | Controls the assistant's personality and rules |
| `print(...)` | Yes (for terminal) | Shows the answer in the console |
| `flask` + `server.py` | Yes (for HTML) | The browser cannot talk to Ollama safely on its own, so it needs an API in the middle |
| `index.html` | Yes (for web UI) | The page where the user types a question |
| `day1` folder | No | Only for organization |

---

## 10. Next Steps

- Add **chat memory** by storing previous messages in the `messages` list
- Add **streaming** (`stream=True`) so the answer appears word by word
- Add **RAG** to answer from your own documents
- Package the app with **Docker** for deployment