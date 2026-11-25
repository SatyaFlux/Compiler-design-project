"""
Structured error definitions for all compiler phases.
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CompilerError:
    error_type: str  # LexicalError | SyntaxError | SemanticError | RuntimeError | GrammarError
    message: str
    line: int = 1
    column: int = 1
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
