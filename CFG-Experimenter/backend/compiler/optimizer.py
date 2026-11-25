"""
TAC Code Optimizer implementing:
1. Constant Folding
2. Constant Propagation
3. Common Subexpression Elimination (CSE)
4. Dead Code Elimination (DCE)
"""
from copy import deepcopy
from typing import Dict, List, Optional, Set, Tuple
from .intermediate import TACInstruction


def _parse_const(token: Optional[str]):
    if token is None:
        return None
    if token == "true":
        return True
    if token == "false":
        return False
    try:
        if "." in token:
            return float(token)
        return int(token)
    except ValueError:
        return None


def _format_const(val) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float) and val.is_integer():
        return str(val)
    return str(val)


def _eval_binop(op: str, a, b):
    try:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                return None
            return a // b if isinstance(a, int) and isinstance(b, int) else a / b
        if op == "%":
            if b == 0 or not (isinstance(a, int) and isinstance(b, int)):
                return None
            return a % b
        if op == "==":
            return a == b
        if op == "!=":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        if op == "&&":
            return bool(a) and bool(b)
        if op == "||":
            return bool(a) or bool(b)
    except Exception:
        return None
    return None


class TACOptimizer:
    """Applies classical compiler optimizations on TAC instructions."""

    def optimize(self, instructions: List[TACInstruction]) -> dict:
        current = deepcopy(instructions)
        passes_applied: List[dict] = []

        # Run up to 3 fixpoint iterations of CF + CP + CSE, then DCE
        for _ in range(3):
            current, cp_count = self._constant_propagation(current)
            if cp_count:
                passes_applied.append({"pass": "Constant Propagation", "changes": cp_count})

            current, cf_count = self._constant_folding(current)
            if cf_count:
                passes_applied.append({"pass": "Constant Folding", "changes": cf_count})

            current, cse_count = self._common_subexpression_elimination(current)
            if cse_count:
                passes_applied.append({"pass": "Common Subexpression Elimination", "changes": cse_count})

            if cp_count == 0 and cf_count == 0 and cse_count == 0:
                break

        current, dce_count = self._dead_code_elimination(current)
        if dce_count:
            passes_applied.append({"pass": "Dead Code Elimination", "changes": dce_count})

        # Renumber lines cleanly
        for idx, instr in enumerate(current, start=1):
            instr.line = idx

        return {
            "original": [i.to_dict() for i in instructions],
            "optimized": [i.to_dict() for i in current],
            "passes_applied": passes_applied,
            "original_count": len(instructions),
            "optimized_count": len(current),
        }

    def _constant_propagation(self, instrs: List[TACInstruction]) -> Tuple[List[TACInstruction], int]:
        consts: Dict[str, str] = {}
        changes = 0
        out: List[TACInstruction] = []

        for instr in instrs:
            inst = deepcopy(instr)
            # Clear constant map at control-flow boundaries (labels/jumps)
            if inst.op in ("label", "goto", "if_false"):
                if inst.op == "if_false" and inst.arg1 in consts:
                    inst.arg1 = consts[inst.arg1]
                    changes += 1
                consts.clear()
                out.append(inst)
                continue

            if inst.arg1 in consts:
                inst.arg1 = consts[inst.arg1]
                changes += 1
            if inst.arg2 in consts:
                inst.arg2 = consts[inst.arg2]
                changes += 1

            if inst.op == "assign" and inst.result:
                if _parse_const(inst.arg1) is not None:
                    consts[inst.result] = inst.arg1
                else:
                    consts.pop(inst.result, None)
            elif inst.result:
                consts.pop(inst.result, None)

            out.append(inst)
        return out, changes

    def _constant_folding(self, instrs: List[TACInstruction]) -> Tuple[List[TACInstruction], int]:
        changes = 0
        out: List[TACInstruction] = []
        for instr in instrs:
            inst = deepcopy(instr)
            if inst.op == "binop":
                v1 = _parse_const(inst.arg1)
                v2 = _parse_const(inst.arg2)
                if v1 is not None and v2 is not None:
                    folded = _eval_binop(inst.operator, v1, v2)
                    if folded is not None:
                        inst = TACInstruction(
                            line=inst.line,
                            op="assign",
                            result=inst.result,
                            arg1=_format_const(folded),
                        )
                        changes += 1
            elif inst.op == "unary":
                v1 = _parse_const(inst.arg1)
                if v1 is not None:
                    if inst.operator == "-" and isinstance(v1, (int, float)):
                        inst = TACInstruction(line=inst.line, op="assign", result=inst.result, arg1=_format_const(-v1))
                        changes += 1
                    elif inst.operator == "!" and isinstance(v1, bool):
                        inst = TACInstruction(line=inst.line, op="assign", result=inst.result, arg1=_format_const(not v1))
                        changes += 1
            out.append(inst)
        return out, changes

    def _common_subexpression_elimination(self, instrs: List[TACInstruction]) -> Tuple[List[TACInstruction], int]:
        expr_map: Dict[Tuple[str, str, str], str] = {}
        changes = 0
        out: List[TACInstruction] = []

        for instr in instrs:
            inst = deepcopy(instr)
            if inst.op in ("label", "goto", "if_false"):
                expr_map.clear()
                out.append(inst)
                continue

            if inst.op == "binop" and inst.operator and inst.arg1 and inst.arg2:
                key = (inst.operator, inst.arg1, inst.arg2)
                if key in expr_map:
                    existing_var = expr_map[key]
                    inst = TACInstruction(
                        line=inst.line,
                        op="assign",
                        result=inst.result,
                        arg1=existing_var,
                    )
                    changes += 1
                else:
                    if inst.result:
                        expr_map[key] = inst.result

            # Invalidate any cached expression using redefined result
            if inst.result:
                to_del = [k for k, v in expr_map.items() if k[1] == inst.result or k[2] == inst.result or v == inst.result]
                for k in to_del:
                    if inst.op == "binop" and k == (inst.operator, inst.arg1, inst.arg2):
                        continue
                    expr_map.pop(k, None)

            out.append(inst)
        return out, changes

    def _dead_code_elimination(self, instrs: List[TACInstruction]) -> Tuple[List[TACInstruction], int]:
        # Remove unused temporary assignments (t1, t2, ...) and self-assignments (x = x)
        used: Set[str] = set()
        for inst in instrs:
            if inst.arg1:
                used.add(inst.arg1)
            if inst.arg2:
                used.add(inst.arg2)

        changes = 0
        out: List[TACInstruction] = []
        for inst in instrs:
            if inst.op == "assign" and inst.result == inst.arg1:
                changes += 1
                continue
            # Only eliminate unused compiler temporaries (t<digits>) safely
            if inst.op in ("assign", "binop", "unary") and inst.result:
                if inst.result.startswith("t") and inst.result[1:].isdigit() and inst.result not in used:
                    changes += 1
                    continue
            out.append(inst)
        return out, changes
