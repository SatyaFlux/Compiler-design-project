"""
Seeds initial preset grammars, sample experiments, learning modules, and quiz questions.
"""
import json
from pathlib import Path
from .db import DB_PATH, get_connection, init_db

PRESET_GRAMMARS = [
    (
        "Arithmetic Expressions (LL(1))",
        "Standard LL(1) expression grammar without left recursion.",
        "E",
        "E -> T E'\nE' -> + T E' | - T E' | ε\nT -> F T'\nT' -> * F T' | / F T' | ε\nF -> ( E ) | id | num",
        "id + num * id",
        1,
    ),
    (
        "Balanced Parentheses",
        "Simple LL(1) grammar for nested parentheses.",
        "S",
        "S -> ( S ) S | ε",
        "( ( ) ) ( )",
        1,
    ),
    (
        "Simple Assignment & Expressions",
        "Assignment statement grammar with arithmetic.",
        "Stmt",
        "Stmt -> id = E ;\nE -> T E'\nE' -> + T E' | ε\nT -> id | num",
        "id = num + id ;",
        1,
    ),
    (
        "Dangling Else (LL(1) Conflict Demo)",
        "Classic ambiguous grammar demonstrating FIRST/FOLLOW conflict.",
        "S",
        "S -> i E t S S' | a\nS' -> e S | ε\nE -> b",
        "i b t a e a",
        1,
    ),
]

SAMPLE_EXPERIMENTS = [
    (
        "Arithmetic & Optimization Demo",
        "a = 10;\nb = 20;\nc = a + b * 2;\nd = a + b * 2;\nprint(c);",
        "E -> T E'\nE' -> + T E' | - T E' | ε\nT -> F T'\nT' -> * F T' | / F T' | ε\nF -> ( E ) | num | id",
        "compiled",
    ),
    (
        "Control Flow (If / While Loop)",
        "int sum = 0;\nint i = 1;\nwhile (i <= 5) {\n    sum = sum + i;\n    i = i + 1;\n}\nif (sum > 10) {\n    print(sum);\n}",
        "E -> T E'\nE' -> + T E' | ε\nT -> num | id",
        "compiled",
    ),
]

MODULE_KEYS = [
    "grammar", "lexer", "syntax", "first_follow", "ll1_table",
    "parse_tree", "ast", "semantic", "intermediate", "optimizer",
    "execution", "errors", "quiz",
]

QUIZ_QUESTIONS = [
    ("Compiler Phases", "Easy", "Which compiler phase groups characters into meaningful tokens?", ["Syntax Analysis", "Lexical Analysis", "Semantic Analysis", "Code Optimization"], 1, "Lexical Analysis (the Scanner/Lexer) reads the character stream and produces tokens."),
    ("Compiler Phases", "Medium", "Which phase is responsible for generating Three-Address Code (TAC)?", ["Lexical Analyzer", "Parser", "Intermediate Code Generator", "Linker"], 2, "Intermediate Code Generation lowers the AST into machine-independent TAC."),
    ("Lexical Analysis", "Easy", "What does a Lexer ignore while scanning source code?", ["Keywords", "Operators", "Whitespace and Comments", "Identifiers"], 2, "Whitespace and comments are stripped unless needed as token separators."),
    ("Lexical Analysis", "Medium", "Which data structure or formal model is primarily used to specify tokens in a Lexer?", ["Pushdown Automaton", "Finite Automaton / Regular Expressions", "Turing Machine", "Context-Free Grammar"], 1, "Tokens are defined using regular expressions and recognized by finite automata."),
    ("Syntax Analysis", "Easy", "What is the primary output of a Syntax Analyzer (Parser)?", ["Token Stream", "Parse Tree / AST", "Machine Code", "Symbol Table"], 1, "The parser verifies grammar structure and constructs a Parse Tree or AST."),
    ("Syntax Analysis", "Medium", "Why must direct left recursion be eliminated before using Recursive Descent or LL(1) parsing?", ["It causes infinite recursion", "It increases memory usage", "It breaks lexical tokens", "It prevents optimization"], 0, "A -> A α causes a top-down parser to call A() indefinitely without consuming input."),
    ("FIRST and FOLLOW", "Medium", "In the grammar S -> A B, A -> a | ε, B -> b, what is FIRST(S)?", ["{a}", "{a, b}", "{a, ε}", "{b}"], 1, "Since A is nullable (A -> ε), FIRST(S) includes FIRST(A)-{ε} = {a} union FIRST(B) = {b}."),
    ("FIRST and FOLLOW", "Medium", "Which symbol is always initially placed in FOLLOW(S) where S is the start symbol?", ["ε", "$", "id", "None"], 1, "The end-of-input marker '$' is always placed in FOLLOW(StartSymbol)."),
    ("LL(1) Parsing", "Medium", "What does the first 'L', second 'L', and '(1)' stand for in LL(1)?", ["Left-to-right scan, Leftmost derivation, 1 lookahead token", "Left-to-right, Last-in-first-out, 1 stack", "Linear, Leftmost, 1 pass", "Lookahead, Leftmost, 1 symbol"], 0, "LL(1) scans Left-to-right, produces a Leftmost derivation, using 1 lookahead token."),
    ("LL(1) Parsing", "Hard", "A grammar is NOT LL(1) if any cell M[A, a] in the parsing table contains:", ["ε", "More than one production", "Only '$'","A terminal symbol"], 1, "Multiple entries in M[A, a] indicate a FIRST/FIRST or FIRST/FOLLOW conflict."),
    ("Parse Tree", "Easy", "In a Parse Tree, what do the leaf nodes represent?", ["Non-terminals", "Terminals (tokens) or ε", "Only operators", "Temporary variables"], 1, "Internal nodes are non-terminals, while leaves are terminals or ε."),
    ("AST", "Medium", "How does an Abstract Syntax Tree (AST) differ from a Concrete Parse Tree?", ["AST omits punctuation/grammar scaffolding like parentheses and semicolons", "AST has more nodes than a Parse Tree", "AST is built by the Lexer", "AST cannot represent expressions"], 0, "An AST captures essential program structure without syntactic sugar/delimiters."),
    ("Semantic Analysis", "Easy", "Which data structure stores variable names, types, and scope information?", ["Parsing Table", "Symbol Table", "Call Stack", "TAC Buffer"], 1, "The Symbol Table tracks identifiers, their types, scopes, and declaration lines."),
    ("Semantic Analysis", "Medium", "Which error is caught during Semantic Analysis rather than Syntax Analysis?", ["Missing semicolon", "Unmatched parenthesis", "Using an undeclared variable", "Invalid character '@'"], 2, "Undeclared variables and type mismatches are semantic errors."),
    ("Intermediate Code", "Medium", "In Three-Address Code (TAC), how many operands can appear on the right-hand side of an instruction at most?", ["One", "Two", "Three", "Unlimited"], 1, "TAC instructions have the form x = y op z (at most two operands and one operator on RHS)."),
    ("Code Optimization", "Easy", "Replacing `t1 = 2 * 3` with `t1 = 6` at compile time is called:", ["Dead Code Elimination", "Constant Folding", "Loop Unrolling", "Register Allocation"], 1, "Constant Folding evaluates constant expressions at compile time."),
    ("Code Optimization", "Medium", "Eliminating an instruction whose result is never used anywhere is called:", ["Constant Propagation", "Common Subexpression Elimination", "Dead Code Elimination", "Strength Reduction"], 2, "Dead Code Elimination removes unreachable or unused assignments."),
]


def seed_db(db_path: Path = DB_PATH) -> None:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()

    if cur.execute("SELECT COUNT(*) FROM grammars").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO grammars (name, description, start_symbol, productions_text, sample_input, is_preset) VALUES (?, ?, ?, ?, ?, ?)",
            PRESET_GRAMMARS,
        )

    if cur.execute("SELECT COUNT(*) FROM experiments").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO experiments (title, source_code, grammar_text, status) VALUES (?, ?, ?, ?)",
            SAMPLE_EXPERIMENTS,
        )

    if cur.execute("SELECT COUNT(*) FROM learning_progress").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO learning_progress (module_key, completed) VALUES (?, 0)",
            [(k,) for k in MODULE_KEYS],
        )

    if cur.execute("SELECT COUNT(*) FROM quiz_questions").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO quiz_questions (topic, difficulty, question, options_json, correct_index, explanation) VALUES (?, ?, ?, ?, ?, ?)",
            [(t, d, q, json.dumps(opts), idx, exp) for (t, d, q, opts, idx, exp) in QUIZ_QUESTIONS],
        )

    conn.commit()
    conn.close()
