# Day 06 — Build Your First RAG System 🔎🧠

Part of the **AI_Agent_Journy** day-by-day learning series.

| Day | Topic |
|-----|-------|
| Day 01 | Ollama chatbot |
| Day 02 | AI assistant with memory |
| Day 03 | Prompt engineering — system prompts & roles |
| Day 04 | AI tools — teach the assistant to use Python functions |
| Day 05 | Document AI — read, summarize, explain and question files |
| **Day 06** | **RAG — find the right document by meaning, then answer from it** |

---

## 🎯 Goal of Day 6

Build a complete **RAG (Retrieval-Augmented Generation)** system from scratch:

- 📚 a **knowledge base** of multiple documents
- 🔤 a **keyword retriever**, and why it isn't enough
- 🧬 **embeddings**, which turn text into numbers that capture **meaning**
- 📐 **cosine similarity**, which measures how close two meanings are
- 🤖 a full **RAG pipeline**: question → find the most relevant document → AI answers **only** from it

On Day 5 **you** had to tell the assistant which file to read (`ask project.txt ...`). On Day 6 **the assistant finds the right file by itself.**

---

## 🤔 What Is RAG?

**RAG = Retrieval-Augmented Generation**

| Word | Meaning | In our code |
|------|---------|-------------|
| **Retrieval** | Find the most relevant information for the question | Embeddings + cosine similarity pick the best `.txt` file |
| **Augmented** | Add that information to the prompt | `Context: {context}` inside the prompt |
| **Generation** | The model writes the answer using that information | `client.chat.completions.create(...)` |

> 📖 **Analogy:** an *open-book exam*.
> The model alone = a student answering from memory, who may confidently guess wrong.
> RAG = the student first **finds the right page in the book**, then answers from that page.

### The RAG pipeline

```
            ┌──────────── ONCE, at start-up ────────────┐
            │                                            │
knowledge/  │  load every .txt  ──►  embedding for each  │
*.txt  ─────┼─►  (retriever.py)       (nomic-embed-text) │
            │                              │             │
            └──────────────────────────────┼─────────────┘
                                           ▼
                               stored document vectors
                                           │
            ┌──────────── EVERY question ──┼─────────────┐
            │                              │             │
 "What is   │  embed the question          │             │
  SQL?" ────┼─► question vector ──► cosine similarity    │
            │                       with every document  │
            │                              │             │
            │                     highest score wins     │
            │                       → mysql.txt          │
            │                              │             │
            │   prompt = instruction + Context + Question│
            │                              │             │
            │                         LLM (MODEL)        │
            │                              │             │
            └──────────────────────────────┼─────────────┘
                                           ▼
                        "SQL is used to query data
                         stored in MySQL tables..."
```

---

## ✅ Why RAG? (Benefits)

| Benefit | Explanation |
|---------|-------------|
| 🔒 **Uses your private data** | The model was never trained on your notes, company docs or project files. RAG lets it answer from them anyway. |
| 🎯 **Fewer hallucinations** | The model answers from real text you give it, not from memory or guesses. |
| 🔄 **Always up to date** | Update a `.txt` file and the next answer uses the new content. **No retraining needed.** |
| 📏 **Scales beyond the context window** | Day 5 sent the **whole** file. RAG sends only the **relevant** part, so you can have many documents. |
| ⚡ **Faster and cheaper** | Smaller prompts mean less processing and fewer tokens (that matters with paid APIs). |
| 🧾 **Traceable answers** | You know exactly which document the answer came from, so you can show the source. |
| 💰 **Cheaper than fine-tuning** | Fine-tuning retrains the model (slow, expensive). RAG just adds a search step. |
| 🔌 **Model-independent** | Swap `llama3.2` ↔ `qwen3:4b` ↔ a cloud model and the knowledge base stays the same. |

## ⚠️ RAG Limitations

| Limitation | Explanation |
|------------|-------------|
| 🗑️ **Garbage in, garbage out** | If retrieval picks the wrong document, the model answers from wrong context, even confidently. |
| 🧩 **Chunking is hard** | Big documents must be split into chunks. Too small loses context; too big adds noise. |
| 🔗 **Multi-document questions** | "Compare Python and MySQL" needs 2 documents. A top-1 retriever only sends one. |
| 🔤 **Exact terms can be missed** | Embeddings capture meaning, but can be weak on exact codes, IDs and names (e.g. `ERR-4012`). Real systems combine keyword + semantic (*hybrid search*). |
| 📏 **Context window still exists** | You can't send unlimited retrieved text. Top-k must stay small. |
| 🐢 **Extra latency** | Every question needs an embedding call plus a search before the answer. |
| 💾 **Index must be maintained** | When documents change, their embeddings must be re-created. |
| 🤥 **Can still hallucinate** | If nothing relevant exists, the model may still invent an answer unless the prompt tells it to say "not found". |
| 📊 **Hard to evaluate** | You must test **both** retrieval (right doc?) and generation (right answer?). |

---

## 🧩 The 5 Parts at a Glance

| Part | Course lessons | What we build | New files |
|------|----------------|---------------|-----------|
| **P1** | 71–74 | **Knowledge base** + load all documents | `knowledge/*.txt`, `retriever.py`, `test_retriever.py` |
| **P2** | 75–76 | **Keyword retriever**: find a document containing a word | `retriever.py` (+ `retrieve()`) |
| **P3** | 77–81 | **Embeddings**: turn text into vectors with Ollama | `test_embedding.py` |
| **P4** | 82–85 | **Cosine similarity**: score how similar two texts are | `similarity.py` |
| **P5** | 86–89 | **Complete RAG app**: semantic retrieval + AI answer | `rag.py`, `test_embedding.py` (now a function) |

---

## 📁 Folder Structure

```
Day_06_RAG/
├── README.md
├── Day06_P1/
│   ├── knowledge/            # the knowledge base
│   │   ├── machine_learning.txt
│   │   ├── mysql.txt
│   │   ├── python.txt
│   │   └── weather.txt
│   ├── retriever.py          # load_documents()
│   └── test_retriever.py
├── Day06_P2/
│   ├── knowledge/
│   ├── retriever.py          # + retrieve() keyword search
│   └── test_retriever.py
├── Day06_P3/
│   ├── knowledge/
│   ├── retriever.py
│   ├── test_retriever.py
│   └── test_embedding.py     # first embeddings
├── Day06_P4/
│   ├── knowledge/
│   ├── retriever.py
│   ├── test_retriever.py
│   ├── similarity.py         # cosine_similarity()
│   └── test_embedding.py     # + similarity score
└── Day06_P5/
    ├── knowledge/
    ├── retriever.py
    ├── test_retriever.py
    ├── similarity.py
    ├── test_embedding.py     # create_embedding() function
    └── rag.py                # the complete RAG app
```

---

## ⚙️ Setup (new for Day 6)

Day 6 needs **two new things**.

**1. An embedding model in Ollama**

```bash
ollama pull nomic-embed-text
ollama list        # should show nomic-embed-text and your chat model
```

**2. `numpy`** for the cosine similarity maths. Add it to the root `requirements.txt`:

```
openai
python-dotenv
numpy
```

```bash
cd "/d/AI Agents/AI_Agent_Journy"
source venv/Scripts/activate
python -m pip install -r requirements.txt
```

> The chat model still comes from the shared root `.env` (`MODEL=...`). The embedding model `nomic-embed-text` is written directly in the code.

---

## ▶️ How to Run

> ⚠️ Run each script **from inside its own part folder**. The code uses the relative path `knowledge/`.

```bash
cd Day_06_RAG/Day06_P1 && python test_retriever.py
cd ../Day06_P2 && python test_retriever.py
cd ../Day06_P3 && python test_embedding.py
cd ../Day06_P4 && python test_embedding.py
cd ../Day06_P5 && python rag.py
```

Type `quit` to exit `rag.py`.

---

## 📚 The Knowledge Base

Four small documents on **different topics**, so it's easy to see whether the retriever picks the right one.

### `knowledge/machine_learning.txt`

```
Machine Learning is a branch of Artificial Intelligence.

It enables computers to learn
from data without being explicitly programmed.
```

### `knowledge/mysql.txt`

```
MySQL is a relational database management system.

It stores structured data
using tables,
rows,
and columns.

SQL is used to query data.
```

### `knowledge/python.txt`

```
Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.
```

### `knowledge/weather.txt`

```
Weather forecasting predicts future atmospheric conditions.

It uses temperature,
humidity,
wind speed,
and pressure.
```

---

# Part 1 — Building the Knowledge Base 📚

**Goal:** put several documents in one folder (the **knowledge base**) and load them **all at once** into Python.

On Day 5 we read **one file by name**. RAG needs to search across **many** files, so first we load everything.

### `retriever.py`

```python
from pathlib import Path

def load_documents():

    documents = {}

    folder = Path("knowledge")

    for file in folder.glob("*.txt"):

        documents[file.name] = file.read_text(
            encoding="utf-8"
        )

    return documents
```

### Step-by-step explanation

| Code | Meaning |
|------|---------|
| `from pathlib import Path` | `pathlib` is Python's modern way to work with files and folders. |
| `documents = {}` | An empty **dictionary**: key = file name, value = file text. |
| `Path("knowledge")` | Points to the `knowledge` folder (relative to where you run the script). |
| `folder.glob("*.txt")` | Finds **every** file ending in `.txt`. `*` means "anything". |
| `file.name` | Just the file name, e.g. `python.txt`. |
| `file.read_text(encoding="utf-8")` | Opens, reads and closes the file in one step. `utf-8` means Bangla, emojis and special characters work. |
| `return documents` | Returns `{"python.txt": "Python is...", "mysql.txt": "MySQL is...", ...}` |

> 💡 **Why a dictionary?** We keep the **file name** together with its **content**, so later we can say *which* document an answer came from.

### `test_retriever.py`

```python
from retriever import load_documents

documents = load_documents()

for name, text in documents.items():

    print(name)

    print(text)

    print("-" * 40)
```

`documents.items()` gives each `(name, text)` pair. The loop prints every document with a separator line.

**Add a document:** drop any new `.txt` file into `knowledge/` and run again. It's loaded automatically, with no code change.

### 📤 Output — Part 1

#### `python test_retriever.py`
```
$ python test_retriever.py
machine_learning.txt
Machine Learning is a branch of Artificial Intelligence.

It enables computers to learn
from data without being explicitly programmed.

----------------------------------------
mysql.txt
MySQL is a relational database management system.

It stores structured data
using tables,
rows,
and columns.

SQL is used to query data.

----------------------------------------
python.txt
Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.

----------------------------------------
weather.txt
Weather forecasting predicts future atmospheric conditions.

It uses temperature,
humidity,
wind speed,
and pressure.

----------------------------------------
```

**Observation:**
<!-- e.g. All 4 documents loaded with their names. -->

---

# Part 2 — Keyword-Based Retriever 🔤

**Goal:** given a search word, find the document that **contains** it.

### `retriever.py`

```python
from pathlib import Path

def load_documents():

    documents = {}

    folder = Path("knowledge")

    for file in folder.glob("*.txt"):

        documents[file.name] = file.read_text(
            encoding="utf-8"
        )

    return documents

def retrieve(question):

    documents = load_documents()

    question = question.lower()

    for filename, content in documents.items():

        if question in content.lower():

            return filename, content

    return None, None
```

### Step-by-step explanation — `retrieve()`

| Code | Meaning |
|------|---------|
| `documents = load_documents()` | Load the whole knowledge base (P1). |
| `question = question.lower()` | Lower-case it, so `Python` = `python`. |
| `for filename, content in documents.items():` | Check each document one by one. |
| `if question in content.lower():` | Does the document's text **contain** the search text? |
| `return filename, content` | Return the **first** match and stop. |
| `return None, None` | Nothing matched. Two `None`s, because the caller expects two values. |

### `test_retriever.py`

P2 searches for `"Python"`:

```python
from retriever import retrieve

filename, content = retrieve("Python")

print(filename)

print()

print(content)
```

P3–P5 search for `"Artificial"`:

```python
from retriever import retrieve

filename, content = retrieve("Artificial")

print(filename)

print()

print(content)
```

### 🧪 Why keyword search isn't enough

Try these searches and see the problems:

| Search | Result | Problem |
|--------|--------|---------|
| `"Python"` | ✅ `python.txt` | Works: the exact word is in the file. |
| `"Artificial"` | ⚠️ Only **one** file | Both `machine_learning.txt` **and** `python.txt` contain it, but only the **first** match is returned. |
| `"What is Python?"` | ❌ `None` | The **whole sentence** must appear in the file, and it doesn't. Real questions fail. |
| `"DB"` | ❌ `None` | `mysql.txt` says "database", but the abbreviation "DB" isn't in the file. |
| `"programming language"` | ⚠️ `python.txt` | Works, but `"coding language"` (same meaning) → ❌ |
| `"rain forecast"` | ❌ `None` | `weather.txt` is clearly about this, but doesn't contain those exact words. |

**The core problem:** keyword search matches **letters**, not **meaning**. *"coding language"* and *"programming language"* mean the same thing but share almost no letters. We need search by **meaning**: **semantic search**.

### 📤 Output — Part 2

#### `retrieve("Python")`
```
$ python test_retriever.py
python.txt

Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.
```

#### `retrieve("Artificial")`
```
 python test_retriever.py
machine_learning.txt

Machine Learning is a branch of Artificial Intelligence.

It enables computers to learn
from data without being explicitly programmed.
```

#### Failing case — e.g. `retrieve("What is Python?")`
```
$ python test_retriever.py
None

None
```

**Observation:**
<!-- e.g. Exact words work; full questions and synonyms return None. -->

---

# Part 3 — Embeddings 🧬

### What is an embedding?

An **embedding** is a list of numbers (a **vector**) that represents the **meaning** of a text.

```
"Python is a programming language."  ──►  [0.021, -0.443, 0.187, ..., 0.092]   (768 numbers)
"Python is used for software dev."   ──►  [0.019, -0.401, 0.205, ..., 0.088]   (very similar!)
"Weather uses humidity and wind."    ──►  [-0.310, 0.122, -0.051, ..., 0.441]  (very different)
```

> 🗺️ **Analogy:** think of a huge map where every sentence is a point. Sentences with **similar meaning are placed close together**, even if they use different words. An embedding is that point's **coordinates**, in 768 dimensions instead of 2.

| Idea | Meaning |
|------|---------|
| Same meaning, different words | → **close** vectors (`car` ≈ `automobile`) |
| Different meaning | → **far** vectors |
| Embedding model | A model trained only to produce these vectors. It **doesn't chat**. |
| `nomic-embed-text` | Free, local embedding model in Ollama. Produces **768** numbers per text. |

> 🔑 **Two different models in RAG:**
> **Embedding model** (`nomic-embed-text`) → turns text into vectors, used for **search**.
> **Chat model** (`llama3.2` / `qwen3:4b`) → writes the **answer**.

### `test_embedding.py`

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


text1 = "Python is a programming language."

text2 = "Python is used for software development."

embedding1 = client.embeddings.create(
    model="nomic-embed-text",
    input=text1
).data[0].embedding

embedding2 = client.embeddings.create(
    model="nomic-embed-text",
    input=text2
).data[0].embedding



print(len(embedding1))
print(len(embedding2))
```

### Step-by-step explanation

| Code | Meaning |
|------|---------|
| `OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` | Same Ollama client as before, but with the URL written directly in the code (not from `.env`). |
| `client.embeddings.create(...)` | Calls the **embeddings** endpoint, not chat. |
| `model="nomic-embed-text"` | The embedding model. |
| `input=text1` | The text to convert. |
| `.data[0].embedding` | The result is a list of objects. Take the first one and get its vector (a Python `list` of floats). |
| `print(len(embedding1))` | Prints the number of dimensions. Expected: **768** for both. |

> Every text, short or long, gets a vector of the **same length** (768). That's what makes vectors comparable.

### 📤 Output — Part 3

#### `python test_embedding.py`
```
$ python test_embedding.py
768
768
```

**Observation:**
<!-- e.g. Both embeddings have 768 numbers. -->

---

# Part 4 — Cosine Similarity 📐

We have two vectors. How do we measure **how similar** they are?

### The idea

Each vector is an **arrow** pointing in some direction. **Cosine similarity** measures the **angle** between two arrows:

```
   same direction           90°                  opposite
       ──►                  ▲                     ──►
       ──►                  │                  ◄──
                            └──►
   score ≈ 1.0          score ≈ 0.0           score ≈ -1.0
   same meaning         unrelated             opposite
```

| Score | Meaning |
|-------|---------|
| close to **1** | Very similar meaning |
| around **0.5** | Somewhat related |
| close to **0** | Unrelated |

> In practice, real text embeddings rarely go negative. What matters is **which score is highest**.

### The formula

```
                     A · B
cos_sim(A, B) = ─────────────
                 ‖A‖ × ‖B‖
```

| Part | Meaning | NumPy |
|------|---------|-------|
| `A · B` | **Dot product**: multiply matching numbers and add them all up | `np.dot(v1, v2)` |
| `‖A‖` | **Length (norm)** of vector A | `np.linalg.norm(v1)` |
| ÷ lengths | Removes the effect of length, so **only direction (meaning)** counts | `/ (...)` |

**Tiny example (2 numbers instead of 768):**

```
A = [1, 2]   B = [2, 4]
A · B = 1×2 + 2×4 = 10
‖A‖ = √(1²+2²) = 2.236    ‖B‖ = √(2²+4²) = 4.472
cos_sim = 10 / (2.236 × 4.472) = 1.0   → same direction
```

### `similarity.py`

```python
import numpy as np

def cosine_similarity(vector1, vector2):

    v1 = np.array(vector1)
    v2 = np.array(vector2)

    return np.dot(v1, v2) / (
        np.linalg.norm(v1) *
        np.linalg.norm(v2)
    )
```

| Code | Meaning |
|------|---------|
| `import numpy as np` | NumPy: a fast maths library for arrays and vectors. |
| `np.array(vector1)` | Converts the Python list into a NumPy array so we can do vector maths. |
| `np.dot(v1, v2)` | Dot product (top of the formula). |
| `np.linalg.norm(v1) * np.linalg.norm(v2)` | Lengths multiplied (bottom of the formula). |

### `test_embedding.py` (P4)

```python
from openai import OpenAI
from similarity import cosine_similarity

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

text1 = "Python is a programming language."

text2 = "Python is used for software development."

embedding1 = client.embeddings.create(
    model="nomic-embed-text",
    input=text1
).data[0].embedding

embedding2 = client.embeddings.create(
    model="nomic-embed-text",
    input=text2
).data[0].embedding



print(len(embedding1))
print(len(embedding2))

score = cosine_similarity(
    embedding1,
    embedding2
)

print(score)
```

Same as P3, plus the last part: compare the two vectors and print the **similarity score**.

### 🧪 Try it

Change `text2` and compare the scores:

| `text2` | Expected score |
|---------|----------------|
| `"Python is used for software development."` | High (same topic) |
| `"Coding in Python is popular."` | High (same meaning, different words) |
| `"Weather forecasting uses humidity."` | Low (unrelated) |

### 📤 Output — Part 4

#### `python test_embedding.py` (related sentences)
```
$ python test_embedding.py
768
768
0.8127294631475279
```

#### Unrelated sentence — change `text2` to a weather sentence
```
768
768
0.3629598929548778
```

**Observation:**
<!-- e.g. Related ≈ 0.8, unrelated ≈ 0.4 → the higher score really means closer meaning. -->

---

# Part 5 — The Complete RAG Application 🤖

Everything comes together:

| Piece | From |
|-------|------|
| Load knowledge base | P1 `retriever.py` → `load_documents()` |
| Text → vector | P5 `test_embedding.py` → `create_embedding()` |
| Score vectors | P4 `similarity.py` → `cosine_similarity()` |
| Answer with context | Day 5's grounding idea + chat model |

### `test_embedding.py` (P5): turned into a reusable function

```python
from openai import OpenAI
from similarity import cosine_similarity

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def create_embedding(content):
    embedding1 = client.embeddings.create(
    model="nomic-embed-text",
    input=content
    ).data[0].embedding
    return embedding1
```

The P3/P4 embedding code is wrapped in a **function**, `create_embedding(content)`. Give it any text and it returns its vector. Now `rag.py` can import it and reuse it for **documents and questions**.

### `rag.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os
from retriever import load_documents

from test_embedding import create_embedding

from similarity import cosine_similarity

documents = load_documents()

document_embeddings = {}

for filename, content in documents.items():

    document_embeddings[filename] = create_embedding(
        content
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

while True:

    user_input = input("\nYou : ")

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    question_embedding = create_embedding(
    user_input)

    best_score = -1

    best_document = None

    for filename, embedding in document_embeddings.items():

        score = cosine_similarity(
        question_embedding,
        embedding
        )

        if score > best_score:

            best_score = score

            best_document = filename

    context = documents[best_document]

    prompt = f"""
Answer the question using only
the following information.

Context:

{context}

Question:

{user_input}
"""


    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("\nAI :", response.choices[0].message.content)
```

### Step-by-step explanation

**Step 1 — Load the knowledge base**

```python
documents = load_documents()
```

**Step 2 — Embed every document (once, at start-up)**

```python
document_embeddings = {}
for filename, content in documents.items():
    document_embeddings[filename] = create_embedding(content)
```

The result is like `{"python.txt": [0.02, ...], "mysql.txt": [-0.31, ...], ...}`. This is our tiny **vector index**. It's done **before** the chat loop, so documents are embedded only once, not for every question.

**Step 3 — Chat client and banner**: same as previous days (`load_dotenv()` → `OpenAI(...)`).

**Step 4 — Embed the question**

```python
question_embedding = create_embedding(user_input)
```

The question goes through the **same** embedding model, so it lands on the same "meaning map" as the documents.

**Step 5 — Find the best document (semantic retrieval)**

```python
best_score = -1
best_document = None

for filename, embedding in document_embeddings.items():
    score = cosine_similarity(question_embedding, embedding)
    if score > best_score:
        best_score = score
        best_document = filename
```

| Code | Meaning |
|------|---------|
| `best_score = -1` | Start lower than any possible score, so the first document always beats it. |
| loop + `cosine_similarity` | Score the question against **every** document. |
| `if score > best_score:` | Keep track of the **highest** score so far. This is a classic "find the maximum" loop. |
| `best_document` | After the loop: the file name of the most similar document. |

**Example:**

```
Question: "Which language is good for AI?"

machine_learning.txt   0.61
mysql.txt              0.38
python.txt             0.74   ← best
weather.txt            0.29
```

**Step 6 — Augment: build the prompt with context**

```python
context = documents[best_document]

prompt = f"""
Answer the question using only
the following information.

Context:
{context}

Question:
{user_input}
"""
```

The **R** (retrieval) is done. This is the **A** (augmented): the best document's text goes into the prompt as `Context`.

**Step 7 — Generate the answer**

```python
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": prompt}]
)
print("\nAI :", response.choices[0].message.content)
```

This is the **G** (generation): the chat model answers using only the given context.

### Keyword (P2) vs Semantic (P5)

| Question | Keyword retriever | Semantic retriever (RAG) |
|----------|-------------------|--------------------------|
| "Python" | ✅ python.txt | ✅ python.txt |
| "What is Python?" | ❌ None | ✅ python.txt |
| "How do I store data in tables?" | ❌ None | ✅ mysql.txt |
| "Will it rain tomorrow?" | ❌ None | ✅ weather.txt |
| "How do computers learn?" | ❌ None | ✅ machine_learning.txt |

### Day 5 vs Day 6

| | Day 5 — Document AI | Day 6 — RAG |
|---|---|---|
| Who picks the file? | **You** (`ask project.txt ...`) | **The assistant** (by meaning) |
| Command format needed? | Yes | No, just ask normally |
| Number of documents | One at a time | Whole knowledge base |
| Search method | None (exact file name) | Embeddings + cosine similarity |

### 📤 Output — Part 5

#### `What is Python used for?`
```
$ python rag.py
========================================
      My AI Assistant
========================================

You : What is Python used for?

AI : Python is used for Artificial Intelligence, Machine Learning, Data Science, Automation, and Web Development.
```

#### `How is data stored in MySQL?`
```
You : How is data stored in MySQL?

AI : Data is stored in MySQL using tables, rows, and columns.
```

#### `What does weather forecasting use?`
```
You : What does weather forecasting use?

AI : Weather forecasting uses:

1. Temperature
2. Humidity
3. Wind speed
4. Pressure
```

#### `How do computers learn without programming?`
```
You : How do computers learn without programming?

AI : Computers learn without programming by using Machine Learning, a branch of Artificial Intelligence.
```

#### Question NOT in the knowledge base — e.g. `Who won the World Cup?`
```
You : Who won the World Cup?

AI : There is no information provided about the World Cup or any other sports-related topic. The conversation is about Machine Learning and Artificial Intelligence, and there is no connection to sports.
```

**Observation:**
<!-- e.g. Picked the right document every time without me naming it. For the World Cup question it still picked a document… see limitations. -->

---

## 🔍 P1 → P5 Comparison

| | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Load many documents | ✅ | ✅ | ✅ | ✅ | ✅ |
| Keyword search | ❌ | ✅ | ✅ | ✅ | ✅ (not used) |
| Embeddings | ❌ | ❌ | ✅ | ✅ | ✅ |
| Similarity score | ❌ | ❌ | ❌ | ✅ | ✅ |
| Finds document by meaning | ❌ | ❌ | ❌ | ❌ | ✅ |
| AI answers from context | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## ⚠️ Known Limitations of This Code / Improvements

1. **Always picks a document, even when none is relevant.** "Who won the World Cup?" still gets the *least bad* document as context. Fix: add a **threshold**, e.g. `if best_score < 0.5: print("I don't have information about that.")`.
2. **No "not found" rule in the prompt.** Day 5 P3 told the model *"If the answer is not available, say: I couldn't find that information."* `rag.py` doesn't, so it may answer from general knowledge. Add that line back.
3. **Only the top 1 document.** A question like *"Compare Python and MySQL"* needs two documents. Fix: sort the scores and send the **top-k** (e.g. top 2).
4. **No chunking.** Each whole file gets one embedding. That's fine for 4-line files, but a 50-page document would be one blurry vector. Real RAG splits documents into chunks (e.g. ~500 characters) and embeds each chunk.
5. **Embeddings are re-created on every run.** With 1,000 documents, start-up would be very slow. Fix: save them to a file, or use a **vector database** (Chroma, FAISS, Qdrant).
6. **The file name `test_embedding.py` is misleading in P5.** It's no longer a test, it's a module. Rename it to `embeddings.py` and update the import in `rag.py`.
7. **The embedding URL and model are hard-coded.** Move them to `.env` (e.g. `EMBED_MODEL=nomic-embed-text`) like the chat model.
8. **No sources shown.** Print `best_document` and `best_score` with each answer. That's great for learning and for debugging wrong answers.
9. **No chat memory and no system prompt.** Each question is independent, so follow-ups like *"tell me more"* don't work.
10. **The keyword `retrieve()` returns only the first match** and needs the **whole** search text to appear in the file.
11. **Empty `knowledge/` folder → crash.** `best_document` stays `None`, so `documents[None]` raises `KeyError`.
12. **Must run from the part folder** because of the relative path `Path("knowledge")`.

### Quick upgrade example (fixes 1, 2 and 8)

```python
if best_score < 0.5:
    print("\nAI : I don't have information about that in my knowledge base.")
    continue

print(f"\n📄 Source: {best_document} (score: {best_score:.2f})")

prompt = f"""
Answer the question using only the following information.
If the answer is not in the information, say:
"I couldn't find that in the knowledge base."

Context:
{context}

Question:
{user_input}
"""
```

> Tune the `0.5` threshold by looking at real scores from your own questions.

---

## ✅ Key Takeaways

- **RAG = Retrieve the right information → Augment the prompt → Generate the answer.**
- Keyword search matches **letters**; semantic search matches **meaning**.
- An **embedding** is a vector of numbers that represents meaning; similar meaning gives close vectors.
- **Cosine similarity** scores how close two vectors are (≈1 = same meaning).
- RAG uses **two models**: an embedding model for search and a chat model for answers.
- Embed documents **once**, embed each question **every time**, and pick the highest score.
- RAG lets an AI answer from **your** private, up-to-date data **without retraining**, but retrieval quality decides answer quality.

---

## ➡️ Next: Day 07
