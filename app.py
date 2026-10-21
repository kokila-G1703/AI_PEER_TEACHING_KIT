import os
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from groq import Groq

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "peer_teaching.db"

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-this-secret")
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS teaching_kits (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                student_label TEXT,
                kit_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                student_label TEXT,
                assessment_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def generate_teaching_kit(topic, level, language):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "replace_with_your_groq_api_key":
        raise RuntimeError("GROQ_API_KEY is missing. Add your key to the .env file and restart the app.")

    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    client = Groq(api_key=api_key)

    system_prompt = """
You are a careful educational assistant creating a peer-teaching kit.
Return ONLY a valid JSON object with these exact top-level keys:
topic, level, language, simple_explanation, misconceptions, lesson_plan, slides,
handout, quiz, verification_checklist, teacher_tips, prompt_used.
Requirements:
- Use the user's requested topic, not a fixed list. If it is ambiguous, state your interpretation in simple_explanation.
- Keep the content age-appropriate, educational, clear and suitable for a 10-minute peer lesson.
- misconceptions: array of 3 objects, each with "misconception" and "correction".
- lesson_plan: array of 4 objects with "time", "activity", "teacher_says".
- slides: exactly 6 objects with "title" and "bullets" (bullets is an array of 2-4 short strings).
- handout: a one-page-style concise text with headings and a short example.
- quiz: exactly 5 objects with "question", "options" (exactly 4 strings), "correct_index" (integer 0-3), and "explanation".
- verification_checklist: array of 4 concrete facts/claims a student should verify with a trustworthy source; do not pretend you checked sources.
- teacher_tips: array of 3 strings.
- prompt_used: a short description of the prompt strategy, not hidden reasoning.
- Never fabricate citations, studies, statistics, or sources. Mark uncertain or fast-changing details as needing verification.
- Do not provide private chain-of-thought. Give concise educational answers only.
"""

    user_prompt = f"""
Create a complete peer-teaching kit.
Topic: {topic}
Learner level: {level}
Output language: {language}
The student needs to teach classmates for about 10 minutes. Include practical examples and one simple activity.
Ensure all JSON values are in the requested language where possible, while retaining standard technical terms.
"""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=4500,
        response_format={"type": "json_object"}
    )
    raw = completion.choices[0].message.content
    data = json.loads(raw)

    # Basic validation so a malformed model response is not shown as a complete kit.
    required = ["topic", "level", "language", "simple_explanation", "misconceptions",
                "lesson_plan", "slides", "handout", "quiz", "verification_checklist",
                "teacher_tips", "prompt_used"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError("The AI response was incomplete. Missing sections: " + ", ".join(missing))
    if not isinstance(data["slides"], list) or len(data["slides"]) != 6:
        raise ValueError("The AI did not return exactly six slides. Please generate the kit again.")
    if not isinstance(data["quiz"], list) or len(data["quiz"]) != 5:
        raise ValueError("The AI did not return exactly five quiz questions. Please generate the kit again.")
    for q in data["quiz"]:
        if not isinstance(q.get("correct_index"), int) or not 0 <= q["correct_index"] <= 3:
            raise ValueError("The quiz contained an invalid answer key. Please generate the kit again.")
        if not isinstance(q.get("options"), list) or len(q["options"]) != 4:
            raise ValueError("A quiz question did not contain four options. Please generate the kit again.")
    return data

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()
    level = request.form.get("level", "Beginner").strip()
    language = request.form.get("language", "Simple English").strip()
    student_label = request.form.get("student_label", "").strip()[:60]

    if not topic:
        flash("Please enter a topic first.", "error")
        return redirect(url_for("index"))
    if len(topic) > 180:
        flash("Please keep the topic under 180 characters.", "error")
        return redirect(url_for("index"))

    try:
        kit = generate_teaching_kit(topic, level, language)
        kit_id = str(uuid.uuid4())
        with get_db() as conn:
            conn.execute(
                "INSERT INTO teaching_kits (id, topic, student_label, kit_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (kit_id, kit["topic"], student_label, json.dumps(kit, ensure_ascii=False), datetime.now().isoformat(timespec="seconds"))
            )
        # Keep only a small ID in the cookie session; the complete AI response stays in SQLite.
        session["current_kit_id"] = kit_id
        session["student_label"] = student_label
        return render_template("result.html", kit=kit, student_label=student_label)
    except Exception as exc:
        # Avoid exposing API credentials or full server internals in the browser.
        message = str(exc)
        if "rate_limit" in message.lower() or "429" in message:
            message = "The free-tier rate limit may have been reached. Wait a little and try again."
        elif "authentication" in message.lower() or "401" in message:
            message = "The API key was rejected. Check GROQ_API_KEY in your .env file."
        elif "model" in message.lower() or "404" in message:
            message = "The selected model may be unavailable. Check the model ID in your Groq console and update GROQ_MODEL."
        else:
            message = message if len(message) < 240 else "Something went wrong while generating the kit. Check your terminal for details."
        app.logger.exception("Teaching-kit generation failed")
        return render_template("index.html", error_message=message, previous_topic=topic), 400

@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    kit_id = session.get("current_kit_id")
    if not kit_id:
        flash("Generate a teaching kit before taking the quiz.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        saved_kit = conn.execute("SELECT kit_json, student_label FROM teaching_kits WHERE id = ?", (kit_id,)).fetchone()
    if not saved_kit:
        flash("Your saved kit could not be found. Please generate it again.", "error")
        return redirect(url_for("index"))
    kit = json.loads(saved_kit["kit_json"])

    assessment_type = request.form.get("assessment_type", "post").lower()
    if assessment_type not in ("pre", "post"):
        assessment_type = "post"
    student_label = session.get("student_label", "")
    score = 0
    questions = kit["quiz"]
    answers = []
    for i, question in enumerate(questions):
        chosen = request.form.get(f"q{i}")
        try:
            chosen_index = int(chosen)
        except (TypeError, ValueError):
            chosen_index = -1
        correct_index = question["correct_index"]
        is_correct = chosen_index == correct_index
        score += int(is_correct)
        answers.append({
            "chosen_index": chosen_index,
            "correct_index": correct_index,
            "is_correct": is_correct,
            "explanation": question["explanation"],
            "question": question["question"]
        })

    with get_db() as conn:
        conn.execute(
            "INSERT INTO quiz_attempts (topic, student_label, assessment_type, score, total, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (kit["topic"], student_label, assessment_type, score, len(questions), datetime.now().isoformat(timespec="seconds"))
        )
    return render_template("quiz_result.html", kit=kit, score=score, total=len(questions),
                           answers=answers, assessment_type=assessment_type)

@app.route("/progress")
def progress():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT topic, student_label, assessment_type, score, total, created_at FROM quiz_attempts ORDER BY id DESC LIMIT 100"
        ).fetchall()
    attempts = [dict(row) for row in rows]
    return render_template("progress.html", attempts=attempts)

@app.route("/download-handout")
def download_handout():
    kit_id = session.get("current_kit_id")
    if not kit_id:
        flash("Generate a kit first to download its handout.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        saved_kit = conn.execute("SELECT kit_json FROM teaching_kits WHERE id = ?", (kit_id,)).fetchone()
    if not saved_kit:
        flash("Your saved kit could not be found. Please generate it again.", "error")
        return redirect(url_for("index"))
    kit = json.loads(saved_kit["kit_json"])
    from flask import Response
    content = f"{kit['topic']}\n{'=' * len(kit['topic'])}\n\nEXPLANATION\n{kit['simple_explanation']}\n\nHANDOUT\n{kit['handout']}\n\nCOMMON MISCONCEPTIONS\n"
    for item in kit["misconceptions"]:
        content += f"- Misconception: {item['misconception']}\n  Correction: {item['correction']}\n"
    content += "\nVERIFY BEFORE TEACHING\n"
    for item in kit["verification_checklist"]:
        content += f"- {item}\n"
    return Response(content, mimetype="text/plain",
                    headers={"Content-Disposition": "attachment; filename=teaching_handout.txt"})

@app.route("/reset")
def reset():
    session.pop("current_kit_id", None)
    session.pop("student_label", None)
    return redirect(url_for("index"))

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
