"""
Experiments, Dashboard Statistics, and Learning Progress API routes.
"""
from flask import Blueprint, jsonify, request
from database.db import get_connection

experiment_bp = Blueprint("experiments", __name__, url_prefix="/api")


@experiment_bp.route("/experiments", methods=["GET"])
def list_experiments():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, source_code, grammar_text, status, created_at, updated_at FROM experiments ORDER BY updated_at DESC, id DESC"
    ).fetchall()
    conn.close()
    return jsonify({"experiments": [dict(r) for r in rows]})


@experiment_bp.route("/experiments", methods=["POST"])
def create_experiment():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled Experiment").strip()
    source_code = data.get("source_code", "")
    grammar_text = data.get("grammar_text", "")
    status = data.get("status", "ready")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO experiments (title, source_code, grammar_text, status) VALUES (?, ?, ?, ?)",
        (title, source_code, grammar_text, status),
    )
    new_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM experiments WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify({"experiment": dict(row)}), 201


@experiment_bp.route("/experiments/<int:exp_id>", methods=["DELETE"])
def delete_experiment(exp_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM experiments WHERE id = ?", (exp_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    if not deleted:
        return jsonify({"error": "Experiment not found"}), 404
    return jsonify({"deleted": True, "id": exp_id})


@experiment_bp.route("/progress", methods=["POST"])
def mark_progress():
    data = request.get_json(silent=True) or {}
    module_key = data.get("module_key")
    completed = 1 if data.get("completed", True) else 0
    if not module_key:
        return jsonify({"error": "module_key is required"}), 400
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO learning_progress (module_key, completed, last_visited)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(module_key) DO UPDATE SET completed = excluded.completed, last_visited = CURRENT_TIMESTAMP
        """,
        (module_key, completed),
    )
    conn.commit()
    conn.close()
    return jsonify({"module_key": module_key, "completed": bool(completed)})


@experiment_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    conn = get_connection()
    exp_count = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
    gram_count = conn.execute("SELECT COUNT(*) FROM grammars").fetchone()[0]
    quiz_attempts = conn.execute("SELECT COUNT(*), COALESCE(AVG(CAST(score AS FLOAT) / NULLIF(total, 0) * 100), 0) FROM quiz_attempts").fetchone()
    progress_rows = conn.execute("SELECT module_key, completed, last_visited FROM learning_progress").fetchall()
    recent_exps = conn.execute(
        "SELECT id, title, source_code, grammar_text, status, updated_at FROM experiments ORDER BY updated_at DESC, id DESC LIMIT 5"
    ).fetchall()
    conn.close()

    progress_list = [dict(r) for r in progress_rows]
    completed_modules = sum(1 for r in progress_list if r["completed"])
    total_modules = len(progress_list) or 13

    return jsonify({
        "stats": {
            "experiments_count": exp_count,
            "grammars_count": gram_count,
            "quiz_attempts": quiz_attempts[0],
            "avg_quiz_score": round(quiz_attempts[1], 1),
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "progress_percent": round((completed_modules / total_modules) * 100),
        },
        "progress": progress_list,
        "recent_experiments": [dict(r) for r in recent_exps],
    })
