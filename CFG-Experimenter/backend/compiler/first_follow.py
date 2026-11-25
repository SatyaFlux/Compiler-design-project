"""
FIRST, FOLLOW, and Nullable computation algorithms with step-by-step traces.
"""
from typing import Dict, List, Set
from .grammar import Grammar, EPSILON


class FirstFollowCalculator:
    """Computes Nullable, FIRST, and FOLLOW sets for a validated Grammar."""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.nullable: Set[str] = set()
        self.first: Dict[str, Set[str]] = {}
        self.follow: Dict[str, Set[str]] = {}
        self.steps: List[dict] = []
        self._compute()

    def _compute(self) -> None:
        nts = self.grammar.non_terminals
        prods = self.grammar.productions
        nt_set = set(nts)

        # 1. Compute Nullable set
        changed = True
        iteration = 0
        while changed:
            changed = False
            iteration += 1
            for lhs in nts:
                if lhs in self.nullable:
                    continue
                for rhs in prods.get(lhs, []):
                    if rhs == [EPSILON] or all(sym in self.nullable for sym in rhs):
                        self.nullable.add(lhs)
                        changed = True
                        self.steps.append({
                            "phase": "Nullable",
                            "iteration": iteration,
                            "symbol": lhs,
                            "rule": f"{lhs} -> {' '.join(rhs)}",
                            "detail": f"Added {lhs} to Nullable",
                        })
                        break

        # 2. Initialize FIRST
        for term in self.grammar.terminals:
            self.first[term] = {term}
        for nt in nts:
            self.first[nt] = set()
            for rhs in prods.get(nt, []):
                if rhs == [EPSILON]:
                    self.first[nt].add(EPSILON)

        # Iterative fixed-point for FIRST
        changed = True
        iteration = 0
        while changed:
            changed = False
            iteration += 1
            for lhs in nts:
                for rhs in prods.get(lhs, []):
                    if rhs == [EPSILON]:
                        continue
                    all_nullable = True
                    for sym in rhs:
                        sym_first = self.first.get(sym, {sym})
                        before = len(self.first[lhs])
                        self.first[lhs] |= (sym_first - {EPSILON})
                        if len(self.first[lhs]) > before:
                            changed = True
                            self.steps.append({
                                "phase": "FIRST",
                                "iteration": iteration,
                                "symbol": lhs,
                                "rule": f"{lhs} -> {' '.join(rhs)}",
                                "detail": f"FIRST({lhs}) now {sorted(self.first[lhs])}",
                            })
                        if sym not in self.nullable and EPSILON not in sym_first:
                            all_nullable = False
                            break
                    if all_nullable and EPSILON not in self.first[lhs]:
                        self.first[lhs].add(EPSILON)
                        changed = True
                        self.steps.append({
                            "phase": "FIRST",
                            "iteration": iteration,
                            "symbol": lhs,
                            "rule": f"{lhs} -> {' '.join(rhs)}",
                            "detail": f"Added ε to FIRST({lhs})",
                        })

        # 3. Initialize FOLLOW
        for nt in nts:
            self.follow[nt] = set()
        if self.grammar.start_symbol:
            self.follow[self.grammar.start_symbol].add("$")
            self.steps.append({
                "phase": "FOLLOW",
                "iteration": 0,
                "symbol": self.grammar.start_symbol,
                "rule": "Start Symbol",
                "detail": f"Added '$' to FOLLOW({self.grammar.start_symbol})",
            })

        # Iterative fixed-point for FOLLOW
        changed = True
        iteration = 0
        while changed:
            changed = False
            iteration += 1
            for lhs in nts:
                for rhs in prods.get(lhs, []):
                    if rhs == [EPSILON]:
                        continue
                    for idx, sym in enumerate(rhs):
                        if sym not in nt_set:
                            continue
                        beta = rhs[idx + 1:]
                        first_beta = self.first_of_sequence(beta)
                        before = len(self.follow[sym])
                        self.follow[sym] |= (first_beta - {EPSILON})
                        if len(self.follow[sym]) > before:
                            changed = True
                            self.steps.append({
                                "phase": "FOLLOW",
                                "iteration": iteration,
                                "symbol": sym,
                                "rule": f"{lhs} -> {' '.join(rhs)}",
                                "detail": f"FOLLOW({sym}) gained {sorted(first_beta - {EPSILON})}",
                            })
                        if not beta or EPSILON in first_beta:
                            before_f = len(self.follow[sym])
                            self.follow[sym] |= self.follow[lhs]
                            if len(self.follow[sym]) > before_f:
                                changed = True
                                self.steps.append({
                                    "phase": "FOLLOW",
                                    "iteration": iteration,
                                    "symbol": sym,
                                    "rule": f"{lhs} -> {' '.join(rhs)}",
                                    "detail": f"FOLLOW({sym}) inherited from FOLLOW({lhs})",
                                })

    def first_of_sequence(self, symbols: List[str]) -> Set[str]:
        """Computes FIRST(α) for any sequence of grammar symbols α."""
        if not symbols or symbols == [EPSILON]:
            return {EPSILON}
        result: Set[str] = set()
        for sym in symbols:
            if sym == EPSILON:
                continue
            sym_first = self.first.get(sym, {sym})
            result |= (sym_first - {EPSILON})
            if EPSILON not in sym_first and sym not in self.nullable:
                return result
        result.add(EPSILON)
        return result

    def to_dict(self) -> dict:
        return {
            "nullable": sorted(self.nullable),
            "first": {nt: sorted(self.first[nt]) for nt in self.grammar.non_terminals},
            "follow": {nt: sorted(self.follow[nt]) for nt in self.grammar.non_terminals},
            "steps": self.steps,
        }
