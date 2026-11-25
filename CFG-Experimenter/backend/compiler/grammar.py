"""
Context-Free Grammar (CFG) Parser and Validator.
Parses productions of the form `A -> B C | ε`, extracts non-terminals and terminals,
detects left recursion, unreachable non-terminals, and unproductive symbols.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Tuple
from .errors import CompilerError

EPSILON_ALIASES = {"ε", "epsilon", "eps", "EPSILON"}
EPSILON = "ε"


@dataclass
class GrammarAnalysis:
    valid: bool
    start_symbol: str
    non_terminals: List[str]
    terminals: List[str]
    productions: Dict[str, List[List[str]]]
    left_recursive: List[str] = field(default_factory=list)
    unreachable: List[str] = field(default_factory=list)
    unproductive: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class Grammar:
    """Represents and validates a Context-Free Grammar."""

    def __init__(self, grammar_text: str):
        self.raw_text = grammar_text or ""
        self.start_symbol: str = ""
        self.non_terminals: List[str] = []
        self.terminals: List[str] = []
        self.productions: Dict[str, List[List[str]]] = {}
        self.errors: List[CompilerError] = []
        self.warnings: List[str] = []
        self._parse()

    def _parse(self) -> None:
        lines = self.raw_text.splitlines()
        ordered_nts: List[str] = []

        for line_no, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            if "->" in line:
                sep = "->"
            elif "::=" in line:
                sep = "::="
            else:
                self.errors.append(
                    CompilerError(
                        error_type="GrammarError",
                        message=f"Missing production arrow '->' or '::=' in '{line}'.",
                        line=line_no,
                        column=1,
                        suggestion="Format productions as: NonTerminal -> symbol1 symbol2 | ε",
                    )
                )
                continue

            lhs_part, rhs_part = line.split(sep, 1)
            lhs = lhs_part.strip()
            if not lhs or " " in lhs:
                self.errors.append(
                    CompilerError(
                        error_type="GrammarError",
                        message=f"Invalid left-hand side '{lhs}' on line {line_no}.",
                        line=line_no,
                        column=1,
                        suggestion="LHS must be a single non-terminal symbol without spaces.",
                    )
                )
                continue

            if not self.start_symbol:
                self.start_symbol = lhs

            if lhs not in self.productions:
                self.productions[lhs] = []
                ordered_nts.append(lhs)

            alternatives = rhs_part.split("|")
            for alt in alternatives:
                alt_stripped = alt.strip()
                if not alt_stripped:
                    self.errors.append(
                        CompilerError(
                            error_type="GrammarError",
                            message=f"Empty alternative in production for '{lhs}'.",
                            line=line_no,
                            column=1,
                            suggestion="Use 'ε' to represent an empty (epsilon) production.",
                        )
                    )
                    continue

                raw_symbols = alt_stripped.split()
                normalized: List[str] = []
                for sym in raw_symbols:
                    if sym in EPSILON_ALIASES:
                        normalized.append(EPSILON)
                    else:
                        normalized.append(sym)

                # Normalize multiple epsilons or epsilon mixed with symbols
                if EPSILON in normalized and len(normalized) > 1:
                    normalized = [s for s in normalized if s != EPSILON] or [EPSILON]

                if normalized not in self.productions[lhs]:
                    self.productions[lhs].append(normalized)
                else:
                    self.warnings.append(
                        f"Duplicate production '{lhs} -> {' '.join(normalized)}' ignored."
                    )

        if not self.productions and not self.errors:
            self.errors.append(
                CompilerError(
                    error_type="GrammarError",
                    message="Grammar is empty. No valid productions found.",
                    line=1,
                    column=1,
                    suggestion="Enter at least one production, e.g. E -> T E'",
                )
            )
            return

        self.non_terminals = ordered_nts
        nt_set = set(self.non_terminals)
        term_list: List[str] = []
        term_set: Set[str] = set()
        for lhs in self.non_terminals:
            for rhs in self.productions[lhs]:
                for sym in rhs:
                    if sym != EPSILON and sym not in nt_set and sym not in term_set:
                        term_set.add(sym)
                        term_list.append(sym)
        self.terminals = term_list

    def detect_left_recursion(self) -> List[str]:
        """Detects direct and indirect left recursion among non-terminals."""
        nt_set = set(self.non_terminals)
        # Build graph of immediate leftmost non-terminal dependencies
        adj: Dict[str, Set[str]] = {nt: set() for nt in self.non_terminals}
        for lhs, alts in self.productions.items():
            for rhs in alts:
                if rhs and rhs[0] in nt_set:
                    adj[lhs].add(rhs[0])

        left_rec: List[str] = []
        for nt in self.non_terminals:
            # BFS/DFS from adj[nt] to see if nt is reachable
            visited = set()
            stack = list(adj[nt])
            while stack:
                curr = stack.pop()
                if curr == nt:
                    left_rec.append(nt)
                    break
                if curr not in visited:
                    visited.add(curr)
                    stack.extend(adj.get(curr, set()))
        return left_rec

    def detect_unreachable(self) -> List[str]:
        """Finds non-terminals not reachable from the start symbol."""
        if not self.start_symbol:
            return []
        nt_set = set(self.non_terminals)
        reachable = {self.start_symbol}
        queue = [self.start_symbol]
        while queue:
            curr = queue.pop(0)
            for rhs in self.productions.get(curr, []):
                for sym in rhs:
                    if sym in nt_set and sym not in reachable:
                        reachable.add(sym)
                        queue.append(sym)
        return [nt for nt in self.non_terminals if nt not in reachable]

    def detect_unproductive(self) -> List[str]:
        """Finds non-terminals that cannot derive any terminal string."""
        nt_set = set(self.non_terminals)
        productive: Set[str] = set()
        changed = True
        while changed:
            changed = False
            for lhs in self.non_terminals:
                if lhs in productive:
                    continue
                for rhs in self.productions.get(lhs, []):
                    if all(sym == EPSILON or sym not in nt_set or sym in productive for sym in rhs):
                        productive.add(lhs)
                        changed = True
                        break
        return [nt for nt in self.non_terminals if nt not in productive]

    def analyze(self) -> GrammarAnalysis:
        left_rec = self.detect_left_recursion() if not self.errors else []
        unreachable = self.detect_unreachable() if not self.errors else []
        unproductive = self.detect_unproductive() if not self.errors else []

        warnings = list(self.warnings)
        if left_rec:
            warnings.append(
                f"Left recursion detected in: {', '.join(left_rec)}. "
                "LL(1) parsing requires eliminating left recursion."
            )
        if unreachable:
            warnings.append(f"Unreachable non-terminals: {', '.join(unreachable)}.")
        if unproductive:
            warnings.append(f"Unproductive non-terminals: {', '.join(unproductive)}.")

        return GrammarAnalysis(
            valid=len(self.errors) == 0,
            start_symbol=self.start_symbol,
            non_terminals=self.non_terminals,
            terminals=self.terminals,
            productions=self.productions,
            left_recursive=left_rec,
            unreachable=unreachable,
            unproductive=unproductive,
            warnings=warnings,
            errors=[e.to_dict() for e in self.errors],
        )
