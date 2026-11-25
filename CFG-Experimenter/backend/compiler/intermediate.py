"""
Three-Address Code (TAC) Generator.
Lowers the AST into linear numbered TAC instructions with temporary variables (t1, t2, ...)
and control-flow labels (L1, L2, ...).
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
from .ast_builder import (
    ASTNode,
    ProgramNode,
    VarDeclNode,
    AssignNode,
    PrintNode,
    BlockNode,
    IfNode,
    WhileNode,
    BinOpNode,
    UnaryOpNode,
    LiteralNode,
    IdentifierNode,
)


@dataclass
class TACInstruction:
    line: int
    op: str          # assign | binop | unary | label | goto | if_false | print
    result: Optional[str] = None
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    operator: Optional[str] = None

    def format(self) -> str:
        if self.op == "assign":
            return f"{self.result} = {self.arg1}"
        if self.op == "binop":
            return f"{self.result} = {self.arg1} {self.operator} {self.arg2}"
        if self.op == "unary":
            return f"{self.result} = {self.operator}{self.arg1}"
        if self.op == "label":
            return f"{self.result}:"
        if self.op == "goto":
            return f"goto {self.result}"
        if self.op == "if_false":
            return f"if_false {self.arg1} goto {self.result}"
        if self.op == "print":
            return f"print {self.arg1}"
        return ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["text"] = self.format()
        return d


class TACGenerator:
    """Generates Three-Address Code from a validated AST."""

    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self._temp_count = 0
        self._label_count = 0

    def _new_temp(self) -> str:
        self._temp_count += 1
        return f"t{self._temp_count}"

    def _new_label(self) -> str:
        self._label_count += 1
        return f"L{self._label_count}"

    def _emit(self, op: str, result=None, arg1=None, arg2=None, operator=None) -> None:
        line_no = len(self.instructions) + 1
        self.instructions.append(
            TACInstruction(
                line=line_no,
                op=op,
                result=result,
                arg1=arg1,
                arg2=arg2,
                operator=operator,
            )
        )

    def generate(self, program: ProgramNode) -> List[TACInstruction]:
        self.instructions = []
        self._temp_count = 0
        self._label_count = 0
        for stmt in program.statements:
            self._gen_stmt(stmt)
        return self.instructions

    def _gen_stmt(self, node: ASTNode) -> None:
        if isinstance(node, VarDeclNode):
            if node.initializer is not None:
                val = self._gen_expr(node.initializer)
                self._emit("assign", result=node.name, arg1=val)
            else:
                self._emit("assign", result=node.name, arg1="0")
        elif isinstance(node, AssignNode):
            val = self._gen_expr(node.value)
            self._emit("assign", result=node.name, arg1=val)
        elif isinstance(node, PrintNode):
            val = self._gen_expr(node.expression)
            self._emit("print", arg1=val)
        elif isinstance(node, BlockNode):
            for s in node.statements:
                self._gen_stmt(s)
        elif isinstance(node, IfNode):
            cond = self._gen_expr(node.condition)
            else_label = self._new_label()
            end_label = self._new_label()
            self._emit("if_false", result=else_label, arg1=cond)
            self._gen_stmt(node.then_branch)
            if node.else_branch is not None:
                self._emit("goto", result=end_label)
            self._emit("label", result=else_label)
            if node.else_branch is not None:
                self._gen_stmt(node.else_branch)
                self._emit("label", result=end_label)
        elif isinstance(node, WhileNode):
            start_label = self._new_label()
            end_label = self._new_label()
            self._emit("label", result=start_label)
            cond = self._gen_expr(node.condition)
            self._emit("if_false", result=end_label, arg1=cond)
            self._gen_stmt(node.body)
            self._emit("goto", result=start_label)
            self._emit("label", result=end_label)
        else:
            self._gen_expr(node)

    def _gen_expr(self, node: ASTNode) -> str:
        if isinstance(node, LiteralNode):
            if node.value_type == "string":
                return f'"{node.value}"'
            if node.value_type == "bool":
                return "true" if node.value else "false"
            return str(node.value)
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, UnaryOpNode):
            operand = self._gen_expr(node.operand)
            t = self._new_temp()
            self._emit("unary", result=t, arg1=operand, operator=node.op)
            return t
        if isinstance(node, BinOpNode):
            left = self._gen_expr(node.left)
            right = self._gen_expr(node.right)
            t = self._new_temp()
            self._emit("binop", result=t, arg1=left, arg2=right, operator=node.op)
            return t
        return "0"
