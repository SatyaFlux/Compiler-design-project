"""
Recursive Descent Parser for the CFG Experimenter mini-language.
Simultaneously constructs a Concrete Parse Tree, an Abstract Syntax Tree (AST),
a step-by-step parsing trace, and detailed SyntaxError diagnostics with recovery.
"""
from typing import List, Optional, Tuple
from .lexer import Token
from .errors import CompilerError
from .parse_tree import ParseTreeBuilder, ParseTreeNode
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

TYPE_KEYWORDS = {"int", "float", "bool", "string", "let"}


class ParseErrorException(Exception):
    """Internal control-flow exception for panic-mode error recovery."""


class RecursiveDescentParser:
    """Top-down Recursive Descent Parser with Parse Tree + AST generation."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[CompilerError] = []
        self.steps: List[dict] = []
        self.pt_builder = ParseTreeBuilder()
        self._step_counter = 0

    def _current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def _record_step(self, rule: str, action: str, node: Optional[ParseTreeNode] = None) -> None:
        self._step_counter += 1
        tok = self._current()
        self.steps.append({
            "step": self._step_counter,
            "rule": rule,
            "action": action,
            "lookahead": tok.lexeme,
            "line": tok.line,
            "column": tok.column,
            "node_id": node.id if node else None,
        })

    def _advance(self, parent_pt: Optional[ParseTreeNode] = None) -> Token:
        tok = self._current()
        if tok.token_type != "EOF":
            self.pos += 1
        if parent_pt is not None:
            term_node = self.pt_builder.make_node(
                label=tok.lexeme,
                node_type="terminal",
                lexeme=tok.lexeme,
                line=tok.line,
                column=tok.column,
            )
            parent_pt.children.append(term_node)
        return tok

    def _expect(self, expected_type: str, expected_lexeme: Optional[str], parent_pt: ParseTreeNode, suggestion: str) -> Token:
        tok = self._current()
        type_ok = tok.token_type == expected_type
        lex_ok = expected_lexeme is None or tok.lexeme == expected_lexeme
        if type_ok and lex_ok:
            self._record_step("Match", f"Matched '{tok.lexeme}'", parent_pt)
            return self._advance(parent_pt)

        expected_desc = f"'{expected_lexeme}'" if expected_lexeme else expected_type
        self.errors.append(
            CompilerError(
                error_type="SyntaxError",
                message=f"Expected {expected_desc}, but found '{tok.lexeme}'.",
                line=tok.line,
                column=tok.column,
                suggestion=suggestion,
            )
        )
        raise ParseErrorException()

    def _synchronize(self) -> None:
        """Panic-mode recovery: advance to next statement boundary."""
        while self._current().token_type != "EOF":
            if self._current().lexeme == ";":
                self._advance()
                return
            if self._current().lexeme in ("}", "if", "while", "print") or self._current().lexeme in TYPE_KEYWORDS:
                return
            self._advance()

    def parse(self) -> Tuple[ProgramNode, ParseTreeNode, List[dict], List[CompilerError]]:
        root_pt = self.pt_builder.make_node("Program", "non_terminal")
        self._record_step("Program -> StmtList", "Start parsing program", root_pt)
        statements: List[ASTNode] = []

        while self._current().token_type != "EOF":
            try:
                stmt_ast, stmt_pt = self._parse_statement()
                root_pt.children.append(stmt_pt)
                if stmt_ast is not None:
                    statements.append(stmt_ast)
            except ParseErrorException:
                self._synchronize()

        eof_tok = self._current()
        root_pt.children.append(
            self.pt_builder.make_node("$", "terminal", "$", eof_tok.line, eof_tok.column)
        )
        self._record_step("Program", "Parsing finished", root_pt)
        return ProgramNode(statements, 1, 1), root_pt, self.steps, self.errors

    def _parse_statement(self) -> Tuple[Optional[ASTNode], ParseTreeNode]:
        tok = self._current()
        stmt_pt = self.pt_builder.make_node("Stmt", "non_terminal")

        if tok.token_type == "KEYWORD" and tok.lexeme in TYPE_KEYWORDS:
            self._record_step("Stmt -> VarDecl", f"Parse variable declaration '{tok.lexeme}'", stmt_pt)
            ast_node, child_pt = self._parse_var_decl()
            stmt_pt.children.append(child_pt)
            return ast_node, stmt_pt

        if tok.token_type == "KEYWORD" and tok.lexeme == "print":
            self._record_step("Stmt -> PrintStmt", "Parse print statement", stmt_pt)
            ast_node, child_pt = self._parse_print()
            stmt_pt.children.append(child_pt)
            return ast_node, stmt_pt

        if tok.token_type == "KEYWORD" and tok.lexeme == "if":
            self._record_step("Stmt -> IfStmt", "Parse if statement", stmt_pt)
            ast_node, child_pt = self._parse_if()
            stmt_pt.children.append(child_pt)
            return ast_node, stmt_pt

        if tok.token_type == "KEYWORD" and tok.lexeme == "while":
            self._record_step("Stmt -> WhileStmt", "Parse while loop", stmt_pt)
            ast_node, child_pt = self._parse_while()
            stmt_pt.children.append(child_pt)
            return ast_node, stmt_pt

        if tok.lexeme == "{":
            self._record_step("Stmt -> Block", "Parse block", stmt_pt)
            ast_node, child_pt = self._parse_block()
            stmt_pt.children.append(child_pt)
            return ast_node, stmt_pt

        if tok.token_type == "IDENTIFIER" and self._peek().lexeme == "=":
            self._record_step("Stmt -> AssignStmt", f"Parse assignment to '{tok.lexeme}'", stmt_pt)
            ast_node, child_pt = self._parse_assign()
            stmt_pt.children.append(child_pt)
            return ast_node, stmt_pt

        # Expression statement fallback
        self._record_step("Stmt -> Expr ;", "Parse expression statement", stmt_pt)
        expr_ast, expr_pt = self._parse_expr()
        stmt_pt.children.append(expr_pt)
        self._expect("DELIMITER", ";", stmt_pt, "Add ';' at the end of the statement.")
        return expr_ast, stmt_pt

    def _parse_var_decl(self) -> Tuple[VarDeclNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("VarDecl", "non_terminal")
        type_tok = self._advance(pt)
        name_tok = self._expect("IDENTIFIER", None, pt, "Provide a valid variable name after the type keyword.")
        init_ast: Optional[ASTNode] = None
        if self._current().lexeme == "=":
            self._advance(pt)
            init_ast, expr_pt = self._parse_expr()
            pt.children.append(expr_pt)
        self._expect("DELIMITER", ";", pt, "Add ';' at the end of the variable declaration.")
        return VarDeclNode(type_tok.lexeme, name_tok.lexeme, init_ast, type_tok.line, type_tok.column), pt

    def _parse_assign(self) -> Tuple[AssignNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("AssignStmt", "non_terminal")
        name_tok = self._advance(pt)
        self._expect("OPERATOR", "=", pt, "Use '=' for variable assignment.")
        val_ast, val_pt = self._parse_expr()
        pt.children.append(val_pt)
        self._expect("DELIMITER", ";", pt, "Add ';' at the end of the assignment.")
        return AssignNode(name_tok.lexeme, val_ast, name_tok.line, name_tok.column), pt

    def _parse_print(self) -> Tuple[PrintNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("PrintStmt", "non_terminal")
        print_tok = self._advance(pt)
        self._expect("DELIMITER", "(", pt, "Add '(' after 'print'.")
        expr_ast, expr_pt = self._parse_expr()
        pt.children.append(expr_pt)
        self._expect("DELIMITER", ")", pt, "Add closing ')' in print statement.")
        self._expect("DELIMITER", ";", pt, "Add ';' after print(...).")
        return PrintNode(expr_ast, print_tok.line, print_tok.column), pt

    def _parse_if(self) -> Tuple[IfNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("IfStmt", "non_terminal")
        if_tok = self._advance(pt)
        self._expect("DELIMITER", "(", pt, "Add '(' after 'if'.")
        cond_ast, cond_pt = self._parse_expr()
        pt.children.append(cond_pt)
        self._expect("DELIMITER", ")", pt, "Add closing ')' after if condition.")
        then_ast, then_pt = self._parse_statement()
        pt.children.append(then_pt)
        else_ast: Optional[ASTNode] = None
        if self._current().token_type == "KEYWORD" and self._current().lexeme == "else":
            self._advance(pt)
            else_ast, else_pt = self._parse_statement()
            pt.children.append(else_pt)
        return IfNode(cond_ast, then_ast, else_ast, if_tok.line, if_tok.column), pt

    def _parse_while(self) -> Tuple[WhileNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("WhileStmt", "non_terminal")
        while_tok = self._advance(pt)
        self._expect("DELIMITER", "(", pt, "Add '(' after 'while'.")
        cond_ast, cond_pt = self._parse_expr()
        pt.children.append(cond_pt)
        self._expect("DELIMITER", ")", pt, "Add closing ')' after while condition.")
        body_ast, body_pt = self._parse_statement()
        pt.children.append(body_pt)
        return WhileNode(cond_ast, body_ast, while_tok.line, while_tok.column), pt

    def _parse_block(self) -> Tuple[BlockNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("Block", "non_terminal")
        open_tok = self._expect("DELIMITER", "{", pt, "Expected '{' to start block.")
        stmts: List[ASTNode] = []
        while self._current().token_type != "EOF" and self._current().lexeme != "}":
            try:
                s_ast, s_pt = self._parse_statement()
                pt.children.append(s_pt)
                if s_ast is not None:
                    stmts.append(s_ast)
            except ParseErrorException:
                self._synchronize()
        self._expect("DELIMITER", "}", pt, "Add closing '}' to terminate block.")
        return BlockNode(stmts, open_tok.line, open_tok.column), pt

    # --- Expression Precedence Climbing ---

    def _parse_expr(self) -> Tuple[ASTNode, ParseTreeNode]:
        pt = self.pt_builder.make_node("Expr", "non_terminal")
        node, child_pt = self._parse_or()
        pt.children.append(child_pt)
        return node, pt

    def _parse_or(self) -> Tuple[ASTNode, ParseTreeNode]:
        left, left_pt = self._parse_and()
        if self._current().lexeme != "||":
            return left, left_pt
        pt = self.pt_builder.make_node("OrExpr", "non_terminal")
        pt.children.append(left_pt)
        while self._current().lexeme == "||":
            op_tok = self._advance(pt)
            right, right_pt = self._parse_and()
            pt.children.append(right_pt)
            left = BinOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
        return left, pt

    def _parse_and(self) -> Tuple[ASTNode, ParseTreeNode]:
        left, left_pt = self._parse_equality()
        if self._current().lexeme != "&&":
            return left, left_pt
        pt = self.pt_builder.make_node("AndExpr", "non_terminal")
        pt.children.append(left_pt)
        while self._current().lexeme == "&&":
            op_tok = self._advance(pt)
            right, right_pt = self._parse_equality()
            pt.children.append(right_pt)
            left = BinOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
        return left, pt

    def _parse_equality(self) -> Tuple[ASTNode, ParseTreeNode]:
        left, left_pt = self._parse_relational()
        if self._current().lexeme not in ("==", "!="):
            return left, left_pt
        pt = self.pt_builder.make_node("EqExpr", "non_terminal")
        pt.children.append(left_pt)
        while self._current().lexeme in ("==", "!="):
            op_tok = self._advance(pt)
            right, right_pt = self._parse_relational()
            pt.children.append(right_pt)
            left = BinOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
        return left, pt

    def _parse_relational(self) -> Tuple[ASTNode, ParseTreeNode]:
        left, left_pt = self._parse_additive()
        if self._current().lexeme not in ("<", ">", "<=", ">="):
            return left, left_pt
        pt = self.pt_builder.make_node("RelExpr", "non_terminal")
        pt.children.append(left_pt)
        while self._current().lexeme in ("<", ">", "<=", ">="):
            op_tok = self._advance(pt)
            right, right_pt = self._parse_additive()
            pt.children.append(right_pt)
            left = BinOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
        return left, pt

    def _parse_additive(self) -> Tuple[ASTNode, ParseTreeNode]:
        left, left_pt = self._parse_multiplicative()
        if self._current().lexeme not in ("+", "-"):
            return left, left_pt
        pt = self.pt_builder.make_node("AddExpr", "non_terminal")
        pt.children.append(left_pt)
        while self._current().lexeme in ("+", "-"):
            op_tok = self._advance(pt)
            right, right_pt = self._parse_multiplicative()
            pt.children.append(right_pt)
            left = BinOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
        return left, pt

    def _parse_multiplicative(self) -> Tuple[ASTNode, ParseTreeNode]:
        left, left_pt = self._parse_unary()
        if self._current().lexeme not in ("*", "/", "%"):
            return left, left_pt
        pt = self.pt_builder.make_node("MulExpr", "non_terminal")
        pt.children.append(left_pt)
        while self._current().lexeme in ("*", "/", "%"):
            op_tok = self._advance(pt)
            right, right_pt = self._parse_unary()
            pt.children.append(right_pt)
            left = BinOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
        return left, pt

    def _parse_unary(self) -> Tuple[ASTNode, ParseTreeNode]:
        if self._current().lexeme in ("!", "-"):
            pt = self.pt_builder.make_node("UnaryExpr", "non_terminal")
            op_tok = self._advance(pt)
            operand, operand_pt = self._parse_unary()
            pt.children.append(operand_pt)
            return UnaryOpNode(op_tok.lexeme, operand, op_tok.line, op_tok.column), pt
        return self._parse_primary()

    def _parse_primary(self) -> Tuple[ASTNode, ParseTreeNode]:
        tok = self._current()
        pt = self.pt_builder.make_node("Primary", "non_terminal")

        if tok.token_type == "INT_LITERAL":
            self._advance(pt)
            return LiteralNode("int", int(tok.lexeme), tok.line, tok.column), pt

        if tok.token_type == "FLOAT_LITERAL":
            self._advance(pt)
            try:
                val = float(tok.lexeme)
            except ValueError:
                val = 0.0
            return LiteralNode("float", val, tok.line, tok.column), pt

        if tok.token_type == "BOOL_LITERAL":
            self._advance(pt)
            return LiteralNode("bool", tok.lexeme == "true", tok.line, tok.column), pt

        if tok.token_type == "STRING_LITERAL":
            self._advance(pt)
            return LiteralNode("string", tok.lexeme, tok.line, tok.column), pt

        if tok.token_type == "IDENTIFIER":
            self._advance(pt)
            return IdentifierNode(tok.lexeme, tok.line, tok.column), pt

        if tok.lexeme == "(":
            self._advance(pt)
            expr_ast, expr_pt = self._parse_expr()
            pt.children.append(expr_pt)
            self._expect("DELIMITER", ")", pt, "Add matching closing parenthesis ')'.")
            return expr_ast, pt

        self.errors.append(
            CompilerError(
                error_type="SyntaxError",
                message=f"Unexpected token '{tok.lexeme}' in expression.",
                line=tok.line,
                column=tok.column,
                suggestion="Expected a number, variable, string, boolean, or '(' expression ')'.",
            )
        )
        raise ParseErrorException()
