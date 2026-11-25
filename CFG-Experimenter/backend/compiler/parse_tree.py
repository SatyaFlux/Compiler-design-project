"""
Parse Tree data structures for both LL(1) CFG parsing and Recursive Descent parsing.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ParseTreeNode:
    id: str
    label: str
    node_type: str = "non_terminal"  # non_terminal | terminal | epsilon
    children: List["ParseTreeNode"] = field(default_factory=list)
    lexeme: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
            "children": [child.to_dict() for child in self.children],
        }


class ParseTreeBuilder:
    """Helper to generate uniquely-ID'd ParseTreeNodes."""

    def __init__(self):
        self._counter = 0

    def next_id(self) -> str:
        self._counter += 1
        return f"pt_{self._counter}"

    def make_node(
        self,
        label: str,
        node_type: str = "non_terminal",
        lexeme: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> ParseTreeNode:
        return ParseTreeNode(
            id=self.next_id(),
            label=label,
            node_type=node_type,
            lexeme=lexeme,
            line=line,
            column=column,
        )
