"""
Abstract Syntax Tree (AST) node definitions and JSON serialization.
"""
from typing import Any, List, Optional


class ASTNode:
    def __init__(self, node_type: str, line: int = 1, column: int = 1):
        self.node_type = node_type
        self.line = line
        self.column = column

    def to_dict(self) -> dict:
        raise NotImplementedError


class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__("Program", line, column)
        self.statements = statements

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "line": self.line,
            "column": self.column,
            "statements": [s.to_dict() for s in self.statements],
        }


class VarDeclNode(ASTNode):
    def __init__(self, var_type: str, name: str, initializer: Optional[ASTNode], line: int, column: int):
        super().__init__("VarDecl", line, column)
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "var_type": self.var_type,
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "initializer": self.initializer.to_dict() if self.initializer else None,
        }


class AssignNode(ASTNode):
    def __init__(self, name: str, value: ASTNode, line: int, column: int):
        super().__init__("Assign", line, column)
        self.name = name
        self.value = value

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "value": self.value.to_dict(),
        }


class PrintNode(ASTNode):
    def __init__(self, expression: ASTNode, line: int, column: int):
        super().__init__("Print", line, column)
        self.expression = expression

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "line": self.line,
            "column": self.column,
            "expression": self.expression.to_dict(),
        }


class BlockNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__("Block", line, column)
        self.statements = statements

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "line": self.line,
            "column": self.column,
            "statements": [s.to_dict() for s in self.statements],
        }


class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: ASTNode, else_branch: Optional[ASTNode], line: int, column: int):
        super().__init__("If", line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "line": self.line,
            "column": self.column,
            "condition": self.condition.to_dict(),
            "then_branch": self.then_branch.to_dict(),
            "else_branch": self.else_branch.to_dict() if self.else_branch else None,
        }


class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode, line: int, column: int):
        super().__init__("While", line, column)
        self.condition = condition
        self.body = body

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "line": self.line,
            "column": self.column,
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict(),
        }


class BinOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode, line: int, column: int):
        super().__init__("BinaryOp", line, column)
        self.op = op
        self.left = left
        self.right = right

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "op": self.op,
            "line": self.line,
            "column": self.column,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }


class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode, line: int, column: int):
        super().__init__("UnaryOp", line, column)
        self.op = op
        self.operand = operand

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "op": self.op,
            "line": self.line,
            "column": self.column,
            "operand": self.operand.to_dict(),
        }


class LiteralNode(ASTNode):
    def __init__(self, value_type: str, value: Any, line: int, column: int):
        super().__init__("Literal", line, column)
        self.value_type = value_type
        self.value = value

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "value_type": self.value_type,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }


class IdentifierNode(ASTNode):
    def __init__(self, name: str, line: int, column: int):
        super().__init__("Identifier", line, column)
        self.name = name

    def to_dict(self) -> dict:
        return {
            "type": self.node_type,
            "name": self.name,
            "line": self.line,
            "column": self.column,
        }
