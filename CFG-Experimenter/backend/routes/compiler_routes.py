"""
Compiler pipeline API routes:
Lexer, Recursive Descent Parser, Parse Tree, AST, Semantic Analysis,
Three-Address Code, Optimizer, Safe Interpreter, and Error Presets.
"""
from flask import Blueprint, jsonify, request
from compiler.lexer import Lexer
from compiler.parser import RecursiveDescentParser
from compiler.semantic import SemanticAnalyzer
from compiler.intermediate import TACGenerator
from compiler.optimizer import TACOptimizer
from compiler.interpreter import SafeInterpreter

compiler_bp = Blueprint("compiler", __name__, url_prefix="/api")

ERROR_PRESETS = [
    {
        "id": "lex_invalid_char",
        "category": "LexicalError",
        "title": "Invalid Character & Unterminated String",
        "description": "Demonstrates illegal '@' symbol and unclosed string literal.",
        "source_code": 'int price = 100;\nstring msg = "Hello Compiler;\nint bad@var = 5;',
    },
    {
        "id": "syn_missing_semi",
        "category": "SyntaxError",
        "title": "Missing Semicolon & Mismatched Parenthesis",
        "description": "Demonstrates syntax errors caught by the Recursive Descent Parser.",
        "source_code": "int a = 10\nint b = (20 + 5;\nprint(b);",
    },
    {
        "id": "sem_type_undeclared",
        "category": "SemanticError",
        "title": "Undefined Variable, Duplicate & Type Mismatch",
        "description": "Demonstrates symbol table and type checking diagnostics.",
        "source_code": 'int x = 10;\nint x = 20;\nint y = "text";\nint z = x + unknownVar;',
    },
    {
        "id": "run_div_zero",
        "category": "RuntimeError",
        "title": "Division by Zero",
        "description": "Syntactically and semantically valid, but fails safely at runtime.",
        "source_code": "int a = 50;\nint b = 0;\nint result = a / b;\nprint(result);",
    },
]


def _run_pipeline(source_code: str, strict_declarations: bool = False) -> dict:
    tokens, lex_errors = Lexer(source_code).tokenize()
    ast, parse_tree, parse_steps, syn_errors = RecursiveDescentParser(tokens).parse()

    all_lex = [e.to_dict() for e in lex_errors]
    all_syn = [e.to_dict() for e in syn_errors]

    semantic_res = {"valid": False, "symbol_table": [], "errors": [], "warnings": []}
    tac_list = []
    opt_res = {"original": [], "optimized": [], "passes_applied": [], "original_count": 0, "optimized_count": 0}
    exec_res = {"status": "skipped", "output": [], "memory": {}, "steps_executed": 0, "errors": []}

    if not all_lex and not all_syn:
        semantic_res = SemanticAnalyzer(strict_declarations=strict_declarations).analyze(ast)
        if semantic_res["valid"]:
            tac_objs = TACGenerator().generate(ast)
            tac_list = [t.to_dict() for t in tac_objs]
            opt_res = TACOptimizer().optimize(tac_objs)
            exec_res = SafeInterpreter().execute(ast)

    all_errors = all_lex + all_syn + semantic_res["errors"] + exec_res["errors"]
    return {
        "tokens": [t.to_dict() for t in tokens],
        "lexical_errors": all_lex,
        "parse_tree": parse_tree.to_dict(),
        "ast": ast.to_dict(),
        "parse_steps": parse_steps,
        "syntax_errors": all_syn,
        "semantic": semantic_res,
        "tac": tac_list,
        "optimization": opt_res,
        "execution": exec_res,
        "errors": all_errors,
        "success": len(all_errors) == 0,
    }


@compiler_bp.route("/lexer/tokenize", methods=["POST"])
def tokenize_code():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    tokens, errors = Lexer(source).tokenize()
    return jsonify({
        "tokens": [t.to_dict() for t in tokens],
        "errors": [e.to_dict() for e in errors],
        "token_count": max(0, len(tokens) - 1),
    })


@compiler_bp.route("/compiler/parse", methods=["POST"])
def parse_code():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    tokens, lex_errors = Lexer(source).tokenize()
    ast, parse_tree, steps, syn_errors = RecursiveDescentParser(tokens).parse()
    return jsonify({
        "tokens": [t.to_dict() for t in tokens],
        "lexical_errors": [e.to_dict() for e in lex_errors],
        "parse_tree": parse_tree.to_dict(),
        "ast": ast.to_dict(),
        "steps": steps,
        "syntax_errors": [e.to_dict() for e in syn_errors],
        "valid": len(lex_errors) == 0 and len(syn_errors) == 0,
    })


@compiler_bp.route("/compiler/semantic", methods=["POST"])
def semantic_check():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    strict = bool(data.get("strict_declarations", False))
    res = _run_pipeline(source, strict_declarations=strict)
    return jsonify({
        "lexical_errors": res["lexical_errors"],
        "syntax_errors": res["syntax_errors"],
        "semantic": res["semantic"],
        "errors": res["lexical_errors"] + res["syntax_errors"] + res["semantic"]["errors"],
    })


@compiler_bp.route("/compiler/tac", methods=["POST"])
def generate_tac():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    res = _run_pipeline(source)
    return jsonify({
        "tac": res["tac"],
        "errors": res["lexical_errors"] + res["syntax_errors"] + res["semantic"]["errors"],
    })


@compiler_bp.route("/compiler/optimize", methods=["POST"])
def optimize_code():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    res = _run_pipeline(source)
    return jsonify({
        "optimization": res["optimization"],
        "errors": res["lexical_errors"] + res["syntax_errors"] + res["semantic"]["errors"],
    })


@compiler_bp.route("/compiler/execute", methods=["POST"])
def execute_code():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    res = _run_pipeline(source)
    return jsonify({
        "execution": res["execution"],
        "errors": res["errors"],
    })


@compiler_bp.route("/compiler/run-all", methods=["POST"])
def run_all():
    data = request.get_json(silent=True) or {}
    source = data.get("source_code", "")
    strict = bool(data.get("strict_declarations", False))
    return jsonify(_run_pipeline(source, strict_declarations=strict))


@compiler_bp.route("/errors/presets", methods=["GET"])
def get_error_presets():
    return jsonify({"presets": ERROR_PRESETS})
