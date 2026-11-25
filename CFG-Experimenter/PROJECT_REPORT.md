# CFG Experimenter — Academic Project Report

**Course:** Compiler Design  
**Team Size:** 4 Members  
**Submission Target:** 5 December 2026  

---

## 1. Executive Summary
CFG Experimenter bridges theoretical Context-Free Grammar analysis (FIRST/FOLLOW, LL(1) Parsing Tables) and practical imperative language compilation (Lexing, Recursive Descent Parsing, AST, Semantic Analysis, Three-Address Code, Optimization, and Safe Interpretation) inside a unified web application.

## 2. System Architecture
- **Frontend:** React 18, Vite, Lucide React, Framer Motion (White `#FFFFFF` + Purple `#8055D9` theme, `prefers-reduced-motion` compliant).
- **Backend:** Python 3, Flask, Flask-CORS, modular `compiler/` engine package.
- **Database:** SQLite (`experiments`, `grammars`, `quiz_questions`, `quiz_attempts`, `learning_progress`).

## 3. Compiler Algorithms Implemented
1. **Lexical Analysis (`lexer.py`)**: Deterministic character scanner tracking line/column coordinates, supporting `int`, `float`, `bool`, `string`, `let`, `if`, `else`, `while`, `print`, comments, and escape sequences.
2. **CFG & LL(1) Engine (`grammar.py`, `first_follow.py`, `parsing_table.py`)**: Detects direct/indirect left recursion, unreachable/unproductive non-terminals, computes Nullable/FIRST/FOLLOW via fixed-point iteration, constructs LL(1) tables with conflict detection, and simulates stack-based parsing.
3. **Recursive Descent Parser (`parser.py`, `parse_tree.py`, `ast_builder.py`)**: Builds both Concrete Parse Trees and typed ASTs with precedence climbing and panic-mode error recovery.
4. **Semantic Analysis (`semantic.py`, `symbol_table.py`)**: Hierarchical scoped symbol table checking declarations, duplicates, and expression type compatibility.
5. **TAC & Optimization (`intermediate.py`, `optimizer.py`)**: Generates linear Three-Address Code and applies Constant Propagation, Constant Folding, Common Subexpression Elimination, and Dead Code Elimination.
6. **Safe Custom Interpreter (`interpreter.py`)**: AST-walking interpreter with bounded execution steps (max 5,000) and division/modulo-by-zero guards, avoiding Python `eval()`.

## 4. Verification & Testing
All 11 automated `pytest` unit and API integration tests pass, covering valid/invalid grammars, LL(1) conflicts, left recursion, lexical/syntax/semantic/runtime errors, TAC optimization, and quiz scoring. The React frontend builds cleanly with `vite build`.
