"""
Safe Custom AST Interpreter.
Executes validated ASTs directly without using Python's eval() or exec().
Enforces step limits to prevent infinite loops and detects runtime errors
such as division by zero and uninitialized variable access.
"""
from typing import Any, Dict, List
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
from .errors import CompilerError


class RuntimeAbort(Exception):
    def __init__(self, error: CompilerError):
        self.error = error


class SafeInterpreter:
    """Executes an AST safely with bounded steps and memory inspection."""

    def __init__(self, max_steps: int = 5000):
        self.max_steps = max_steps
        self.steps_executed = 0
        self.memory: Dict[str, Any] = {}
        self.output: List[str] = []

    def execute(self, program: ProgramNode) -> dict:
        self.steps_executed = 0
        self.memory = {}
        self.output = []
        errors: List[dict] = []

        try:
            for stmt in program.statements:
                self._exec_stmt(stmt)
            status = "success"
        except RuntimeAbort as abort:
            errors.append(abort.error.to_dict())
            status = "runtime_error"

        return {
            "status": status,
            "output": self.output,
            "memory": {k: self._serialize_val(v) for k, v in self.memory.items()},
            "steps_executed": self.steps_executed,
            "errors": errors,
        }

    def _tick(self, node: ASTNode) -> None:
        self.steps_executed += 1
        if self.steps_executed > self.max_steps:
            raise RuntimeAbort(
                CompilerError(
                    error_type="RuntimeError",
                    message=f"Execution exceeded maximum limit of {self.max_steps} steps (possible infinite loop).",
                    line=node.line,
                    column=node.column,
                    suggestion="Check loop termination conditions in your while loop.",
                )
            )

    def _exec_stmt(self, node: ASTNode) -> None:
        self._tick(node)
        if isinstance(node, VarDeclNode):
            if node.initializer is not None:
                self.memory[node.name] = self._eval_expr(node.initializer)
            else:
                defaults = {"int": 0, "float": 0.0, "bool": False, "string": "", "let": 0}
                self.memory[node.name] = defaults.get(node.var_type, 0)
        elif isinstance(node, AssignNode):
            self.memory[node.name] = self._eval_expr(node.value)
        elif isinstance(node, PrintNode):
            val = self._eval_expr(node.expression)
            self.output.append(self._format_output(val))
        elif isinstance(node, BlockNode):
            for s in node.statements:
                self._exec_stmt(s)
        elif isinstance(node, IfNode):
            cond = self._eval_expr(node.condition)
            if bool(cond):
                self._exec_stmt(node.then_branch)
            elif node.else_branch is not None:
                self._exec_stmt(node.else_branch)
        elif isinstance(node, WhileNode):
            while bool(self._eval_expr(node.condition)):
                self._tick(node)
                self._exec_stmt(node.body)
        else:
            self._eval_expr(node)

    def _eval_expr(self, node: ASTNode) -> Any:
        self._tick(node)
        if isinstance(node, LiteralNode):
            return node.value
        if isinstance(node, IdentifierNode):
            if node.name not in self.memory:
                raise RuntimeAbort(
                    CompilerError(
                        error_type="RuntimeError",
                        message=f"Variable '{node.name}' referenced before assignment at runtime.",
                        line=node.line,
                        column=node.column,
                        suggestion=f"Assign a value to '{node.name}' before reading it.",
                    )
                )
            return self.memory[node.name]
        if isinstance(node, UnaryOpNode):
            val = self._eval_expr(node.operand)
            if node.op == "-":
                return -val
            if node.op == "!":
                return not bool(val)
        if isinstance(node, BinOpNode):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            op = node.op
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    raise RuntimeAbort(
                        CompilerError(
                            error_type="RuntimeError",
                            message="Division by zero.",
                            line=node.line,
                            column=node.column,
                            suggestion="Ensure the divisor is non-zero before dividing.",
                        )
                    )
                if isinstance(left, int) and isinstance(right, int):
                    return left // right
                return left / right
            if op == "%":
                if right == 0:
                    raise RuntimeAbort(
                        CompilerError(
                            error_type="RuntimeError",
                            message="Modulo by zero.",
                            line=node.line,
                            column=node.column,
                            suggestion="Ensure the modulo divisor is non-zero.",
                        )
                    )
                return left % right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == "<":
                return left < right
            if op == ">":
                return left > right
            if op == "<=":
                return left <= right
            if op == ">=":
                return left >= right
            if op == "&&":
                return bool(left) and bool(right)
            if op == "||":
                return bool(left) or bool(right)
        return None

    @staticmethod
    def _format_output(val: Any) -> str:
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)

    @staticmethod
    def _serialize_val(val: Any) -> dict:
        if isinstance(val, bool):
            t = "bool"
        elif isinstance(val, int):
            t = "int"
        elif isinstance(val, float):
            t = "float"
        else:
            t = "string"
        return {"value": val, "type": t}
