"""
Interactive Quiz System API routes.
"""
import json
from flask import Blueprint, jsonify, request
from database.db import get_connection

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")


@quiz_bp.route("/questions", methods=["GET"])
def get_questions():
    topic = request.args.get("topic")
    conn = get_connection()
    if topic and topic != "All":
        rows = conn.execute(
            "SELECT id, topic, difficulty, question, options_json FROM quiz_questions WHERE topic = ? ORDER BY id ASC",
            (topic,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, topic, difficulty, question, options_json FROM quiz_questions ORDER BY id ASC"
        ).fetchall()

    topics_rows = conn.execute("SELECT DISTINCT topic FROM quiz_questions ORDER BY topic ASC").fetchall()
    conn.close()

    questions = []
    for r in rows:
        questions.append({
            "id": r["id"],
            "topic": r["topic"],
            "difficulty": r["difficulty"],
            "question": r["question"],
            "options": json.loads(r["options_json"]),
        })
    return jsonify({
        "topics": ["All"] + [t["topic"] for t in topics_rows],
        "questions": questions,
    })


@quiz_bp.route("/submit", methods=["POST"])
def submit_quiz():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})  # { str(question_id): selected_index }
    topic = data.get("topic", "All")

    conn = get_connection()
    rows = conn.execute("SELECT id, topic, question, options_json, correct_index, explanation FROM quiz_questions").fetchall()

    q_map = {str(r["id"]): dict(r) for r in rows}
    results = []
    score = 0
    total = len(answers)

    for qid_str, selected_idx in answers.items():
        q = q_map.get(str(qid_str))
        if not q:
            continue
        is_correct = int(selected_idx) == int(q["correct_index"])
        if is_correct:
            score += 1
        results.append({
            "question_id": q["id"],
            "question": q["question"],
            "selected_index": int(selected_idx),
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
            "options": json.loads(q["options_json"]),
        })

    if total > 0:
        conn.execute(
            "INSERT INTO quiz_attempts (topic, score, total, answers_json) VALUES (?, ?, ?, ?)",
            (topic, score, total, json.dumps(answers)),
        )
        conn.commit()
    conn.close()

    return jsonify({
        "score": score,
        "total": total,
        "percentage": round((score / total) * 100, 1) if total else 0,
        "results": results,
    })


@quiz_bp.route("/history", methods=["GET"])
def quiz_history():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, topic, score, total, completed_at FROM quiz_attempts ORDER BY id DESC LIMIT 15"
    ).fetchall()
    conn.close()
    return jsonify({"history": [dict(r) for r in rows]})
