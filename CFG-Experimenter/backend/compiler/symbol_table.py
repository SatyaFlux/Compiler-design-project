"""
Scoped Symbol Table for Semantic Analysis.
Tracks variable name, declared/inferred type, scope level, declaration line,
initialization status, and implicit vs explicit declaration.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class SymbolEntry:
    name: str
    var_type: str
    scope_level: int
    line: int
    column: int
    initialized: bool = False
    implicit: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class SymbolTable:
    """Hierarchical scoped symbol table."""

    def __init__(self):
        self.scopes: List[Dict[str, SymbolEntry]] = [{}]
        self.history: List[SymbolEntry] = []

    @property
    def current_level(self) -> int:
        return len(self.scopes) - 1

    def enter_scope(self) -> None:
        self.scopes.append({})

    def exit_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(
        self,
        name: str,
        var_type: str,
        line: int,
        column: int,
        initialized: bool = False,
        implicit: bool = False,
    ) -> bool:
        """Declares symbol in current scope. Returns False if duplicate in same scope."""
        current = self.scopes[-1]
        if name in current:
            return False
        entry = SymbolEntry(
            name=name,
            var_type=var_type,
            scope_level=self.current_level,
            line=line,
            column=column,
            initialized=initialized,
            implicit=implicit,
        )
        current[name] = entry
        self.history.append(entry)
        return True

    def lookup(self, name: str) -> Optional[SymbolEntry]:
        """Looks up symbol from innermost scope outward."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def all_symbols(self) -> List[dict]:
        return [entry.to_dict() for entry in self.history]
