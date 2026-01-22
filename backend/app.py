from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, bcrypt, uuid, os, sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from ai_module.full_pipeline import analyze_sentiment, extract_topics, chatbot_summary

app = Flask(__name__)
CORS(app)

def get_db():
    return sqlite3.connect("database.db")

@app.route("/")
def home():
    return jsonify({"status": "Backend running"})


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT password, role FROM users WHERE username=?", (data["username"],))
    row = cur.fetchone()
    con.close()

    if not row:
        return jsonify({"error": "Invalid credentials"}), 401

    stored, role = row
    if bcrypt.checkpw(data["password"].encode(), stored):
        return jsonify({"message": "Login success", "role": role})

    return jsonify({"error": "Invalid credentials"}), 401


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

    try:
        con = get_db()
        con.execute(
            "INSERT INTO users (username,password,role) VALUES (?,?,?)",
            (data["username"], hashed, "student")
        )
        con.commit()
        con.close()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "User exists"}), 409


# ---------------- FEEDBACK ----------------
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    d = request.json

    sentiment = analyze_sentiment(d["comment"])
    topics = extract_topics(d["comment"])

    con = get_db()
    con.execute(
        "INSERT INTO feedback VALUES (?,?,?,?,?,?,?)",
        (
            str(uuid.uuid4()),
            d["course"],
            d["rating"],
            d["comment"],
            sentiment["score"],
            ",".join(topics),
            datetime.now().strftime("%Y-%m-%d")
        )
    )
    con.commit()
    con.close()

    return jsonify({"message": "Feedback saved"})


# ---------------- ANALYTICS ----------------
@app.route("/analytics")
def analytics():
    con = get_db()
    rows = con.execute(
        "SELECT course,rating,comment,sentiment_score,topics,date FROM feedback"
    ).fetchall()
    con.close()

    records = []
    for r in rows:
        records.append({
            "course": r[0],
            "rating": r[1],
            "comment": r[2],
            "sentiment_score": r[3],
            "topics": r[4].split(","),
            "date": r[5]
        })

    return jsonify({
        "raw_feedback": records,
        "summary": chatbot_summary(records)
    })

# ================= CHATBOT API =================
@app.route("/chatbot", methods=["GET"])
def chatbot():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT comment, date FROM feedback")
    rows = cur.fetchall()
    con.close()

    feedback_records = [{"comment": r[0], "date": r[1]} for r in rows]

    summary = chatbot_summary(feedback_records)

    return jsonify(summary)


if __name__ == "__main__":
    app.run(debug=True)

