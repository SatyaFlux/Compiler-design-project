"""
Semantic Analyzer:
- Variable declaration & duplicate declaration checking
- Undefined variable detection
- Static & inferred type checking (int, float, bool, string)
- Invalid operation detection (e.g., string + int, bool * int, !int)
"""
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
from .symbol_table import SymbolTable
from .errors import CompilerError


NUMERIC_TYPES = {"int", "float"}


class SemanticAnalyzer:
    """Walks the AST to validate declarations, scopes, and types."""

    def __init__(self, strict_declarations: bool = False):
        self.symbol_table = SymbolTable()
        self.errors: List[CompilerError] = []
        self.warnings: List[str] = []
        self.strict_declarations = strict_declarations

    def analyze(self, program: ProgramNode) -> dict:
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []

        for stmt in program.statements:
            self._visit(stmt)

        return {
            "valid": len(self.errors) == 0,
            "symbol_table": self.symbol_table.all_symbols(),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
        }

    def _visit(self, node: ASTNode) -> Optional[str]:
        if isinstance(node, VarDeclNode):
            return self._visit_var_decl(node)
        if isinstance(node, AssignNode):
            return self._visit_assign(node)
        if isinstance(node, PrintNode):
            self._visit(node.expression)
            return None
        if isinstance(node, BlockNode):
            self.symbol_table.enter_scope()
            for s in node.statements:
                self._visit(s)
            self.symbol_table.exit_scope()
            return None
        if isinstance(node, IfNode):
            cond_type = self._visit(node.condition)
            if cond_type and cond_type not in ("bool", "int"):
                self.errors.append(
                    CompilerError(
                        error_type="SemanticError",
                        message=f"If condition must be boolean, got '{cond_type}'.",
                        line=node.condition.line,
                        column=node.condition.column,
                        suggestion="Use a comparison (==, <, >) or boolean expression.",
                    )
                )
            self._visit(node.then_branch)
            if node.else_branch:
                self._visit(node.else_branch)
            return None
        if isinstance(node, WhileNode):
            cond_type = self._visit(node.condition)
            if cond_type and cond_type not in ("bool", "int"):
                self.errors.append(
                    CompilerError(
                        error_type="SemanticError",
                        message=f"While condition must be boolean, got '{cond_type}'.",
                        line=node.condition.line,
                        column=node.condition.column,
                        suggestion="Use a comparison or boolean expression in while(...).",
                    )
                )
            self._visit(node.body)
            return None
        if isinstance(node, BinOpNode):
            return self._visit_binop(node)
        if isinstance(node, UnaryOpNode):
            return self._visit_unary(node)
        if isinstance(node, LiteralNode):
            return node.value_type
        if isinstance(node, IdentifierNode):
            entry = self.symbol_table.lookup(node.name)
            if entry is None:
                self.errors.append(
                    CompilerError(
                        error_type="SemanticError",
                        message=f"Undefined variable '{node.name}'.",
                        line=node.line,
                        column=node.column,
                        suggestion=f"Declare '{node.name}' before using it (e.g., int {node.name} = 0;).",
                    )
                )
                return None
            if not entry.initialized:
                self.warnings.append(
                    f"Line {node.line}: Variable '{node.name}' may be used before initialization."
                )
            return entry.var_type
        return None

    def _visit_var_decl(self, node: VarDeclNode) -> None:
        init_type: Optional[str] = None
        if node.initializer is not None:
            init_type = self._visit(node.initializer)

        resolved_type = node.var_type
        if resolved_type == "let":
            resolved_type = init_type or "int"

        ok = self.symbol_table.declare(
            name=node.name,
            var_type=resolved_type,
            line=node.line,
            column=node.column,
            initialized=node.initializer is not None,
            implicit=False,
        )
        if not ok:
            self.errors.append(
                CompilerError(
                    error_type="SemanticError",
                    message=f"Duplicate declaration of variable '{node.name}' in the same scope.",
                    line=node.line,
                    column=node.column,
                    suggestion=f"Remove the duplicate declaration or rename '{node.name}'.",
                )
            )
            return

        if node.var_type != "let" and init_type is not None:
            if not self._is_assignable(resolved_type, init_type):
                self.errors.append(
                    CompilerError(
                        error_type="SemanticError",
                        message=f"Type mismatch: cannot assign '{init_type}' to '{resolved_type}' variable '{node.name}'.",
                        line=node.line,
                        column=node.column,
                        suggestion=f"Provide a '{resolved_type}' expression or change the variable type.",
                    )
                )

    def _visit_assign(self, node: AssignNode) -> None:
        val_type = self._visit(node.value)
        entry = self.symbol_table.lookup(node.name)
        if entry is None:
            if self.strict_declarations:
                self.errors.append(
                    CompilerError(
                        error_type="SemanticError",
                        message=f"Undeclared variable '{node.name}' in assignment.",
                        line=node.line,
                        column=node.column,
                        suggestion=f"Declare '{node.name}' first using 'let {node.name} = ...' or 'int {node.name} = ...'.",
                    )
                )
                return
            inferred = val_type or "int"
            self.symbol_table.declare(
                name=node.name,
                var_type=inferred,
                line=node.line,
                column=node.column,
                initialized=True,
                implicit=True,
            )
            return

        entry.initialized = True
        if val_type and not self._is_assignable(entry.var_type, val_type):
            self.errors.append(
                CompilerError(
                    error_type="SemanticError",
                    message=f"Type mismatch: cannot assign '{val_type}' to '{entry.var_type}' variable '{node.name}'.",
                    line=node.line,
                    column=node.column,
                    suggestion=f"Ensure the right-hand side evaluates to '{entry.var_type}'.",
                )
            )

    def _visit_binop(self, node: BinOpNode) -> Optional[str]:
        lt = self._visit(node.left)
        rt = self._visit(node.right)
        if lt is None or rt is None:
            return None

        op = node.op
        if op in ("+", "-", "*", "/", "%"):
            if op == "+" and lt == "string" and rt == "string":
                return "string"
            if lt in NUMERIC_TYPES and rt in NUMERIC_TYPES:
                if op == "%" and (lt != "int" or rt != "int"):
                    self.errors.append(
                        CompilerError(
                            error_type="SemanticError",
                            message=f"Modulo '%' requires integer operands, got '{lt}' and '{rt}'.",
                            line=node.line,
                            column=node.column,
                            suggestion="Use integer operands with '%'.",
                        )
                    )
                    return None
                return "float" if "float" in (lt, rt) else "int"
            self.errors.append(
                CompilerError(
                    error_type="SemanticError",
                    message=f"Invalid operands for '{op}': '{lt}' and '{rt}'.",
                    line=node.line,
                    column=node.column,
                    suggestion=f"Operator '{op}' requires numeric operands.",
                )
            )
            return None

        if op in ("<", ">", "<=", ">="):
            if lt in NUMERIC_TYPES and rt in NUMERIC_TYPES:
                return "bool"
            self.errors.append(
                CompilerError(
                    error_type="SemanticError",
                    message=f"Cannot compare '{lt}' and '{rt}' with '{op}'.",
                    line=node.line,
                    column=node.column,
                    suggestion="Relational operators require numeric operands.",
                )
            )
            return None

        if op in ("==", "!="):
            if lt == rt or (lt in NUMERIC_TYPES and rt in NUMERIC_TYPES):
                return "bool"
            self.errors.append(
                CompilerError(
                    error_type="SemanticError",
                    message=f"Incompatible types for '{op}': '{lt}' and '{rt}'.",
                    line=node.line,
                    column=node.column,
                    suggestion="Compare values of compatible types.",
                )
            )
            return None

        if op in ("&&", "||"):
            if lt == "bool" and rt == "bool":
                return "bool"
            self.errors.append(
                CompilerError(
                    error_type="SemanticError",
                    message=f"Logical operator '{op}' requires boolean operands, got '{lt}' and '{rt}'.",
                    line=node.line,
                    column=node.column,
                    suggestion="Use boolean expressions with '&&' and '||'.",
                )
            )
            return None

        return None

    def _visit_unary(self, node: UnaryOpNode) -> Optional[str]:
        ot = self._visit(node.operand)
        if ot is None:
            return None
        if node.op == "-" and ot in NUMERIC_TYPES:
            return ot
        if node.op == "!" and ot == "bool":
            return "bool"
        self.errors.append(
            CompilerError(
                error_type="SemanticError",
                message=f"Invalid unary operator '{node.op}' for type '{ot}'.",
                line=node.line,
                column=node.column,
                suggestion="Use '-' with numbers and '!' with booleans.",
            )
        )
        return None

    @staticmethod
    def _is_assignable(target_type: str, value_type: str) -> bool:
        if target_type == value_type:
            return True
        if target_type == "float" and value_type == "int":
            return True
        return False
