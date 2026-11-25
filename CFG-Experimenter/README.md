# CFG Experimenter — Interactive Compiler Design Teaching Simulator

**CFG Experimenter** is a full-stack educational Compiler Design platform built with **React.js (Vite)**, **Python (Flask)**, and **SQLite**. It implements real compiler algorithms end-to-end with a modern **White + Purple** interactive UI.

## Features (14 Modules)
1. **Dashboard** — Learning progress tracker, statistics cards, quick module launcher, and saved experiments.
2. **Grammar Editor** — Edit/add/delete CFG productions, load presets, detect left recursion, unreachable & unproductive symbols.
3. **Lexical Analyzer** — Character-by-character scanner with line/column tracking, comment/string handling, and lexical error diagnostics.
4. **Syntax Analyzer** — Recursive Descent Parser with step-by-step grammar rule trace and panic-mode error recovery.
5. **FIRST & FOLLOW** — Iterative fixed-point computation of Nullable, FIRST, and FOLLOW sets with step trace.
6. **LL(1) Parsing Table** — Predictive table builder, FIRST/FIRST & FIRST/FOLLOW conflict detection, and `Stack | Input | Action` simulation.
7. **Parse Tree Visualization** — Interactive expandable tree with Play/Pause/Stop/Reset and speed controls.
8. **Abstract Syntax Tree (AST)** — Structural AST explorer with JSON view toggle.
9. **Semantic Analyzer & Symbol Table** — Scoped symbol table, duplicate/undeclared variable detection, and type checking.
10. **Intermediate Code Generation (TAC)** — Numbered Three-Address Code with temporaries and control-flow labels.
11. **Code Optimization** — Constant Propagation, Constant Folding, Common Subexpression Elimination (CSE), and Dead Code Elimination (DCE) with side-by-side comparison.
12. **Code Execution** — Safe custom AST interpreter (zero `eval()`) with step limit, division-by-zero protection, stdout console, and memory table.
13. **Error Simulator** — Curated Lexical, Syntax, Semantic, and Runtime error scenarios with fix suggestions.
14. **Interactive Quiz** — 17+ questions across 10 compiler topics with instant scoring, explanations, and attempt history.

## Installation & Running

### 1. Backend (Flask + SQLite)
```powershell
cd CFG-Experimenter/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Backend runs at `http://127.0.0.1:5000`.

### 2. Frontend (React + Vite)
```powershell
cd CFG-Experimenter/frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173` (proxying `/api` to Flask).

### 3. Running Tests
```powershell
cd CFG-Experimenter/backend
.\.venv\Scripts\pytest.exe tests -v
```

### 4. Deploy on Vercel (One-Click Full-Stack)
This repository is pre-configured with `vercel.json`, `requirements.txt`, and `api/index.py` at the repository root:
1. Go to [vercel.com](https://vercel.com) and click **Add New → Project**.
2. Import your GitHub repository (`Compiler-design-project`).
3. Leave the **Root Directory** as `.` (default) — Vercel automatically detects `vercel.json` to build `CFG-Experimenter/frontend` and deploy the Flask API at `/api/*`.
4. Click **Deploy**.

