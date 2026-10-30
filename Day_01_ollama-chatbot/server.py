import os
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)
MODEL = os.getenv("MODEL")

DB_FILE = "chat.db"
MAX_HISTORY = 20  # how many previous messages are sent to the model as context
SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Answer clearly. "
    "Use Markdown for lists, tables and code blocks."
)

app = Flask(__name__)


# ---------- Database helpers ----------
def query(sql, args=(), one=False, commit=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql, args)
        if commit:
            conn.commit()
            return cur.lastrowid
        rows = cur.fetchall()
        if one:
            return rows[0] if rows else None
        return rows
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New chat',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


# ---------- Page ----------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# ---------- Chat list ----------
@app.get("/api/chats")
def list_chats():
    rows = query("SELECT id, title FROM chats ORDER BY updated_at DESC, id DESC")
    return jsonify([dict(r) for r in rows])


@app.post("/api/chats")
def create_chat():
    chat_id = query("INSERT INTO chats (title) VALUES ('New chat')", commit=True)
    return jsonify({"id": chat_id, "title": "New chat"})


@app.get("/api/chats/<int:chat_id>")
def get_chat(chat_id):
    chat = query("SELECT id, title FROM chats WHERE id = ?", (chat_id,), one=True)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    msgs = query(
        "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id", (chat_id,)
    )
    return jsonify({"id": chat["id"], "title": chat["title"], "messages": [dict(m) for m in msgs]})


@app.delete("/api/chats/<int:chat_id>")
def delete_chat(chat_id):
    query("DELETE FROM messages WHERE chat_id = ?", (chat_id,), commit=True)
    query("DELETE FROM chats WHERE id = ?", (chat_id,), commit=True)
    return jsonify({"ok": True})


# ---------- Send a message (streamed) ----------
@app.post("/api/chats/<int:chat_id>/messages")
def send_message(chat_id):
    text = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not text:
        return jsonify({"error": "Message is required"}), 400

    chat = query("SELECT id, title FROM chats WHERE id = ?", (chat_id,), one=True)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Save the user's message
    query(
        "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
        (chat_id, "user", text),
        commit=True,
    )

    # First message becomes the chat title
    if chat["title"] == "New chat":
        title = text[:40] + ("…" if len(text) > 40 else "")
        query("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id), commit=True)
    query("UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (chat_id,), commit=True)

    # Load the latest messages so the model "remembers" the conversation
    rows = query(
        "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
        (chat_id, MAX_HISTORY),
    )
    history = [dict(r) for r in reversed(rows)]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    def generate():
        parts = []
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    parts.append(delta)
                    yield delta
        except Exception as e:
            yield f"\n\n⚠️ Error: {e}"
        finally:
            # Save the answer (also saves partial text if the user pressed Stop)
            answer = "".join(parts).strip()
            if answer:
                query(
                    "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                    (chat_id, "assistant", answer),
                    commit=True,
                )
                query(
                    "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (chat_id,),
                    commit=True,
                )

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)