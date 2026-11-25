"""
Vercel Serverless WSGI entry point for the CFG Experimenter Flask backend.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "CFG-Experimenter" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app

app = create_app()
