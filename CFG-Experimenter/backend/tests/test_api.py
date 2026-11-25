"""
API endpoint & SQLite integration tests using Flask test_client().
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app


def get_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health_and_dashboard():
    client = get_client()
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

    d = client.get("/api/dashboard/stats")
    assert d.status_code == 200
    data = d.get_json()
    assert data["stats"]["experiments_count"] >= 2
    assert data["stats"]["grammars_count"] >= 4


def test_grammar_and_ll1_endpoints():
    client = get_client()
    cfg = "E -> T E'\nE' -> + T E' | ε\nT -> id | num"

    r1 = client.post("/api/grammar/validate", json={"grammar_text": cfg})
    assert r1.status_code == 200
    assert r1.get_json()["valid"] is True

    r2 = client.post("/api/grammar/first-follow", json={"grammar_text": cfg})
    assert r2.status_code == 200
    assert "E" in r2.get_json()["first"]

    r3 = client.post("/api/grammar/ll1-parse", json={"grammar_text": cfg, "input_string": "id + num"})
    assert r3.status_code == 200
    assert r3.get_json()["accepted"] is True


def test_full_compiler_pipeline_endpoint():
    client = get_client()
    src = "a = 10;\nb = 20;\nc = a + b * 2;\nprint(c);"
    r = client.post("/api/compiler/run-all", json={"source_code": src})
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert data["execution"]["output"] == ["50"]
    assert len(data["tac"]) >= 3
    assert data["optimization"]["optimized_count"] <= data["optimization"]["original_count"]


def test_quiz_endpoints():
    client = get_client()
    r = client.get("/api/quiz/questions")
    assert r.status_code == 200
    qs = r.get_json()["questions"]
    assert len(qs) >= 10

    sub = client.post("/api/quiz/submit", json={"topic": "All", "answers": {str(qs[0]["id"]): 0}})
    assert sub.status_code == 200
    assert "score" in sub.get_json()
