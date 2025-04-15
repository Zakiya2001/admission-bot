
from flask import Flask, request, jsonify, render_template
import requests
import sqlite3

app = Flask(__name__)

RASA_SERVER_URL = "https://your-rasa-url.onrender.com/webhooks/rest/webhook"  # <-- عدليه لاحقاً

def init_db():
    conn = sqlite3.connect('chatlog.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_question(message):
    conn = sqlite3.connect('chatlog.db')
    c = conn.cursor()
    c.execute("INSERT INTO questions_log (question) VALUES (?)", (message,))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    user_message = request.json.get("message", "")
    save_question(user_message)
    try:
        response = requests.post(RASA_SERVER_URL, json={"sender": "user", "message": user_message})
        response.raise_for_status()
        messages = response.json()
        reply = messages[0].get("text", "ما قدرت أفهم سؤالك.") if messages else "ما قدرت أفهم سؤالك."
    except:
        reply = "في مشكلة في الاتصال بالسيرفر. جرّب لاحقاً."
    return jsonify({"response": reply})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
