"""
CFG Grammar, FIRST/FOLLOW, LL(1) Parsing Table, and Stack Simulation API routes.
"""
from flask import Blueprint, jsonify, request
from compiler.grammar import Grammar
from compiler.first_follow import FirstFollowCalculator
from compiler.parsing_table import LL1ParsingTable
from database.db import get_connection

grammar_bp = Blueprint("grammar", __name__, url_prefix="/api/grammar")


@grammar_bp.route("/presets", methods=["GET"])
def list_presets():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, description, start_symbol, productions_text, sample_input, is_preset FROM grammars ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return jsonify({"presets": [dict(r) for r in rows]})


@grammar_bp.route("/validate", methods=["POST"])
def validate_grammar():
    data = request.get_json(silent=True) or {}
    grammar_text = data.get("grammar_text", "")
    g = Grammar(grammar_text)
    return jsonify(g.analyze().to_dict())


@grammar_bp.route("/first-follow", methods=["POST"])
def compute_first_follow():
    data = request.get_json(silent=True) or {}
    grammar_text = data.get("grammar_text", "")
    g = Grammar(grammar_text)
    analysis = g.analyze()
    if not analysis.valid:
        return jsonify({"valid": False, "errors": analysis.errors, "first": {}, "follow": {}, "nullable": [], "steps": []}), 400
    ff = FirstFollowCalculator(g)
    return jsonify({"valid": True, "analysis": analysis.to_dict(), **ff.to_dict()})


@grammar_bp.route("/ll1-table", methods=["POST"])
def build_ll1_table():
    data = request.get_json(silent=True) or {}
    grammar_text = data.get("grammar_text", "")
    g = Grammar(grammar_text)
    analysis = g.analyze()
    if not analysis.valid:
        return jsonify({"valid": False, "errors": analysis.errors}), 400
    table = LL1ParsingTable(g)
    return jsonify({"valid": True, "analysis": analysis.to_dict(), **table.to_dict()})


@grammar_bp.route("/ll1-parse", methods=["POST"])
def simulate_ll1_parse():
    data = request.get_json(silent=True) or {}
    grammar_text = data.get("grammar_text", "")
    input_string = data.get("input_string", "")
    g = Grammar(grammar_text)
    analysis = g.analyze()
    if not analysis.valid:
        return jsonify({"valid": False, "errors": analysis.errors}), 400
    table = LL1ParsingTable(g)
    sim = table.simulate(input_string)
    return jsonify({"valid": True, "table": table.to_dict(), **sim})
