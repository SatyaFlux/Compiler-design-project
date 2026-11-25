"""
LL(1) Parsing Table construction, conflict detection, and stack-based parsing simulation.
"""
from typing import Dict, List, Tuple
from .grammar import Grammar, EPSILON
from .first_follow import FirstFollowCalculator
from .parse_tree import ParseTreeBuilder, ParseTreeNode


class LL1ParsingTable:
    """Builds an LL(1) parsing table and simulates stack-based parsing."""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.ff = FirstFollowCalculator(grammar)
        self.terminals = list(grammar.terminals) + ["$"]
        # table[non_terminal][terminal] = list of RHS productions (len > 1 => conflict)
        self.table: Dict[str, Dict[str, List[List[str]]]] = {
            nt: {t: [] for t in self.terminals} for nt in grammar.non_terminals
        }
        self.conflicts: List[dict] = []
        self.is_ll1: bool = True
        self._build_table()

    def _build_table(self) -> None:
        for lhs in self.grammar.non_terminals:
            for rhs in self.grammar.productions.get(lhs, []):
                first_alpha = self.ff.first_of_sequence(rhs)
                for term in first_alpha - {EPSILON}:
                    if term in self.table[lhs]:
                        if rhs not in self.table[lhs][term]:
                            self.table[lhs][term].append(rhs)

                if EPSILON in first_alpha:
                    for b in self.ff.follow[lhs]:
                        if b in self.table[lhs]:
                            if rhs not in self.table[lhs][b]:
                                self.table[lhs][b].append(rhs)

        # Detect conflicts
        for nt in self.grammar.non_terminals:
            for term in self.terminals:
                entries = self.table[nt][term]
                if len(entries) > 1:
                    self.is_ll1 = False
                    self.conflicts.append({
                        "non_terminal": nt,
                        "terminal": term,
                        "productions": [f"{nt} -> {' '.join(rhs)}" for rhs in entries],
                        "type": "FIRST/FOLLOW" if [EPSILON] in entries else "FIRST/FIRST",
                    })

    def to_dict(self) -> dict:
        formatted_table: Dict[str, Dict[str, List[str]]] = {}
        for nt in self.grammar.non_terminals:
            formatted_table[nt] = {}
            for term in self.terminals:
                formatted_table[nt][term] = [
                    f"{nt} -> {' '.join(rhs)}" for rhs in self.table[nt][term]
                ]
        return {
            "is_ll1": self.is_ll1,
            "non_terminals": self.grammar.non_terminals,
            "terminals": self.terminals,
            "table": formatted_table,
            "conflicts": self.conflicts,
            "first": {nt: sorted(self.ff.first[nt]) for nt in self.grammar.non_terminals},
            "follow": {nt: sorted(self.ff.follow[nt]) for nt in self.grammar.non_terminals},
        }

    def simulate(self, input_string: str, max_steps: int = 500) -> dict:
        """
        Runs stack-based LL(1) predictive parsing on space-separated input tokens.
        Returns Stack | Input | Action trace and a constructed Parse Tree.
        """
        if not self.grammar.start_symbol:
            return {"accepted": False, "error": "Grammar has no start symbol.", "steps": [], "parse_tree": None}

        if not self.is_ll1:
            return {
                "accepted": False,
                "error": "Grammar is not LL(1); resolve parsing table conflicts before simulating.",
                "steps": [],
                "parse_tree": None,
            }

        raw_tokens = [tok for tok in (input_string or "").strip().split() if tok]
        input_tokens = raw_tokens + ["$"]

        builder = ParseTreeBuilder()
        root = builder.make_node(self.grammar.start_symbol, "non_terminal")

        # Stack holds tuples of (symbol, ParseTreeNode | None)
        stack: List[Tuple[str, ParseTreeNode | None]] = [("$", None), (self.grammar.start_symbol, root)]
        cursor = 0
        steps: List[dict] = []
        nt_set = set(self.grammar.non_terminals)
        accepted = False
        error_msg = None

        for step_num in range(1, max_steps + 1):
            top_sym, top_node = stack[-1]
            lookahead = input_tokens[cursor] if cursor < len(input_tokens) else "$"
            stack_str = " ".join(s for s, _ in stack)
            input_str = " ".join(input_tokens[cursor:])

            if top_sym == "$" and lookahead == "$":
                steps.append({
                    "step": step_num,
                    "stack": stack_str,
                    "input": input_str,
                    "action": "ACCEPT",
                    "active_node_id": None,
                })
                accepted = True
                break

            if top_sym not in nt_set:
                # Terminal or '$'
                if top_sym == lookahead:
                    stack.pop()
                    cursor += 1
                    steps.append({
                        "step": step_num,
                        "stack": stack_str,
                        "input": input_str,
                        "action": f"Match '{lookahead}'",
                        "active_node_id": top_node.id if top_node else None,
                    })
                else:
                    error_msg = f"Syntax Error at token '{lookahead}': expected '{top_sym}'."
                    steps.append({
                        "step": step_num,
                        "stack": stack_str,
                        "input": input_str,
                        "action": f"ERROR: expected '{top_sym}', found '{lookahead}'",
                        "active_node_id": top_node.id if top_node else None,
                    })
                    break
            else:
                # Non-terminal
                entries = self.table.get(top_sym, {}).get(lookahead, [])
                if not entries:
                    expected = [t for t, prods in self.table[top_sym].items() if prods]
                    error_msg = (
                        f"Syntax Error at token '{lookahead}': no LL(1) entry for "
                        f"M[{top_sym}, {lookahead}]. Expected one of {expected}."
                    )
                    steps.append({
                        "step": step_num,
                        "stack": stack_str,
                        "input": input_str,
                        "action": f"ERROR: M[{top_sym}, {lookahead}] is empty",
                        "active_node_id": top_node.id if top_node else None,
                    })
                    break

                rhs = entries[0]
                stack.pop()
                if rhs == [EPSILON]:
                    eps_node = builder.make_node(EPSILON, "epsilon")
                    if top_node:
                        top_node.children.append(eps_node)
                    steps.append({
                        "step": step_num,
                        "stack": stack_str,
                        "input": input_str,
                        "action": f"Output {top_sym} -> ε",
                        "active_node_id": top_node.id if top_node else None,
                    })
                else:
                    child_nodes: List[Tuple[str, ParseTreeNode]] = []
                    for sym in rhs:
                        ntype = "non_terminal" if sym in nt_set else "terminal"
                        cnode = builder.make_node(sym, ntype)
                        if top_node:
                            top_node.children.append(cnode)
                        child_nodes.append((sym, cnode))
                    for sym, cnode in reversed(child_nodes):
                        stack.append((sym, cnode))
                    steps.append({
                        "step": step_num,
                        "stack": stack_str,
                        "input": input_str,
                        "action": f"Output {top_sym} -> {' '.join(rhs)}",
                        "active_node_id": top_node.id if top_node else None,
                    })
        else:
            error_msg = "Parsing exceeded maximum step limit (possible infinite loop)."

        return {
            "accepted": accepted,
            "error": error_msg,
            "steps": steps,
            "parse_tree": root.to_dict(),
        }
