"""
Comprehensive unit tests for all CFG Experimenter compiler engine modules.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compiler.lexer import Lexer
from compiler.grammar import Grammar, EPSILON
from compiler.first_follow import FirstFollowCalculator
from compiler.parsing_table import LL1ParsingTable
from compiler.parser import RecursiveDescentParser
from compiler.semantic import SemanticAnalyzer
from compiler.intermediate import TACGenerator
from compiler.optimizer import TACOptimizer
from compiler.interpreter import SafeInterpreter


def test_lexer_valid_and_errors():
    src = 'int x = 10;\nfloat y = 3.14;\n// comment\nprint(x + y);'
    tokens, errors = Lexer(src).tokenize()
    assert not errors
    types = [t.token_type for t in tokens[:-1]]
    assert types == [
        "KEYWORD", "IDENTIFIER", "OPERATOR", "INT_LITERAL", "DELIMITER",
        "KEYWORD", "IDENTIFIER", "OPERATOR", "FLOAT_LITERAL", "DELIMITER",
        "KEYWORD", "DELIMITER", "IDENTIFIER", "OPERATOR", "IDENTIFIER", "DELIMITER", "DELIMITER",
    ]
    assert tokens[0].line == 1 and tokens[0].column == 1
    assert tokens[5].line == 2 and tokens[5].column == 1

    # Lexical errors
    _, bad_errors = Lexer('int a = 1.2.3;\n@').tokenize()
    assert len(bad_errors) == 2
    assert bad_errors[0].error_type == "LexicalError"


def test_grammar_first_follow_ll1():
    cfg = """
    E -> T E'
    E' -> + T E' | - T E' | ε
    T -> F T'
    T' -> * F T' | / F T' | ε
    F -> ( E ) | id | num
    """
    g = Grammar(cfg)
    analysis = g.analyze()
    assert analysis.valid
    assert not analysis.left_recursive
    assert not analysis.unreachable
    assert not analysis.unproductive

    ff = FirstFollowCalculator(g)
    assert "E'" in ff.nullable
    assert "T'" in ff.nullable
    assert "E" not in ff.nullable
    assert ff.first["E"] == {"(", "id", "num"}
    assert ff.follow["E"] == {")", "$"}
    assert ff.follow["E'"] == {")", "$"}
    assert ff.follow["T"] == {"+", "-", ")", "$"}

    table = LL1ParsingTable(g)
    assert table.is_ll1
    assert not table.conflicts

    sim = table.simulate("id + num * id")
    assert sim["accepted"] is True
    assert sim["parse_tree"]["label"] == "E"
    assert len(sim["steps"]) > 0

    bad_sim = table.simulate("id + * num")
    assert bad_sim["accepted"] is False
    assert bad_sim["error"] is not None


def test_ll1_conflict_and_left_recursion_detection():
    ambiguous_cfg = """
    S -> i E t S S' | a
    S' -> e S | ε
    E -> b
    """
    g = Grammar(ambiguous_cfg)
    table = LL1ParsingTable(g)
    assert not table.is_ll1
    assert len(table.conflicts) == 1
    assert table.conflicts[0]["non_terminal"] == "S'"
    assert table.conflicts[0]["terminal"] == "e"

    left_rec_cfg = """
    E -> E + T | T
    T -> num
    """
    g2 = Grammar(left_rec_cfg)
    assert "E" in g2.analyze().left_recursive


def test_parser_ast_and_syntax_errors():
    src = """
    int a = 10;
    int b = 20;
    int c = a + b * 2;
    if (c > 30) {
        print(c);
    }
    """
    tokens, lex_errs = Lexer(src).tokenize()
    assert not lex_errs
    ast, pt, steps, syn_errs = RecursiveDescentParser(tokens).parse()
    assert not syn_errs
    assert pt.label == "Program"
    assert len(ast.statements) == 4
    assert len(steps) > 0

    # Missing semicolon & parenthesis mismatch
    bad_tokens, _ = Lexer("int x = (1 + 2;").tokenize()
    _, _, _, bad_errs = RecursiveDescentParser(bad_tokens).parse()
    assert len(bad_errs) >= 1
    assert bad_errs[0].error_type == "SyntaxError"


def test_semantic_analyzer_and_symbol_table():
    valid_src = "int a = 5;\nfloat b = a + 2.5;\nprint(b);"
    tokens, _ = Lexer(valid_src).tokenize()
    ast, _, _, _ = RecursiveDescentParser(tokens).parse()
    sem = SemanticAnalyzer().analyze(ast)
    assert sem["valid"] is True
    assert len(sem["symbol_table"]) == 2

    # Undefined variable, duplicate declaration, type mismatch
    err_src = 'int a = 5;\nint a = 10;\nint x = "hello";\nint y = z + 1;'
    t2, _ = Lexer(err_src).tokenize()
    ast2, _, _, _ = RecursiveDescentParser(t2).parse()
    sem2 = SemanticAnalyzer().analyze(ast2)
    assert sem2["valid"] is False
    assert len(sem2["errors"]) == 3


def test_tac_and_optimizer():
    src = """
    a = 10;
    b = 20;
    c = a + b * 2;
    d = a + b * 2;
    print(c);
    """
    tokens, _ = Lexer(src).tokenize()
    ast, _, _, _ = RecursiveDescentParser(tokens).parse()
    tac = TACGenerator().generate(ast)
    assert len(tac) >= 5
    opt = TACOptimizer().optimize(tac)
    # 10 + 20 * 2 folds to 50!
    opt_texts = [i["text"] for i in opt["optimized"]]
    assert any("50" in t for t in opt_texts)
    assert len(opt["passes_applied"]) >= 1


def test_interpreter_execution_and_div_by_zero():
    src = """
    int a = 10;
    int b = 20;
    int c = a + b * 2;
    print(c);
    """
    tokens, _ = Lexer(src).tokenize()
    ast, _, _, _ = RecursiveDescentParser(tokens).parse()
    res = SafeInterpreter().execute(ast)
    assert res["status"] == "success"
    assert res["output"] == ["50"]
    assert res["memory"]["c"]["value"] == 50

    # Division by zero
    div_src = "int a = 10 / 0;"
    t2, _ = Lexer(div_src).tokenize()
    ast2, _, _, _ = RecursiveDescentParser(t2).parse()
    res2 = SafeInterpreter().execute(ast2)
    assert res2["status"] == "runtime_error"
    assert res2["errors"][0]["error_type"] == "RuntimeError"
    assert "Division by zero" in res2["errors"][0]["message"]
