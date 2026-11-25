"""
Custom character-by-character Lexical Analyzer.
Tracks exact line and column numbers, detects keywords, identifiers,
numbers (int/float), strings, booleans, operators, delimiters, comments,
and reports detailed lexical errors with suggestions.
"""
from dataclasses import dataclass, asdict
from typing import List, Tuple
from .errors import CompilerError


KEYWORDS = {
    "int", "float", "bool", "string", "let",
    "if", "else", "while", "print", "return",
}
BOOL_LITERALS = {"true", "false"}

TWO_CHAR_OPERATORS = {"==", "!=", "<=", ">=", "&&", "||"}
SINGLE_CHAR_OPERATORS = {"+", "-", "*", "/", "%", "=", "<", ">", "!"}
DELIMITERS = {"(", ")", "{", "}", ";", ","}


@dataclass
class Token:
    token_type: str
    lexeme: str
    line: int
    column: int

    def to_dict(self) -> dict:
        return asdict(self)


class Lexer:
    """Character-by-character scanner for the CFG Experimenter language."""

    def __init__(self, source: str):
        self.source = source or ""
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[CompilerError] = []

    def _current(self) -> str:
        if self.pos >= len(self.source):
            return "\0"
        return self.source[self.pos]

    def _peek(self, offset: int = 1) -> str:
        idx = self.pos + offset
        if idx >= len(self.source):
            return "\0"
        return self.source[idx]

    def _advance(self) -> str:
        ch = self._current()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            ch = self._current()
            if ch in (" ", "\t", "\r", "\n"):
                self._advance()
            elif ch == "/" and self._peek() == "/":
                # Single-line comment
                while self.pos < len(self.source) and self._current() != "\n":
                    self._advance()
            elif ch == "/" and self._peek() == "*":
                # Multi-line comment
                start_line, start_col = self.line, self.column
                self._advance()  # /
                self._advance()  # *
                closed = False
                while self.pos < len(self.source):
                    if self._current() == "*" and self._peek() == "/":
                        self._advance()
                        self._advance()
                        closed = True
                        break
                    self._advance()
                if not closed:
                    self.errors.append(
                        CompilerError(
                            error_type="LexicalError",
                            message="Unterminated multi-line comment.",
                            line=start_line,
                            column=start_col,
                            suggestion="Add closing '*/' to terminate the comment.",
                        )
                    )
            else:
                break

    def _scan_identifier_or_keyword(self) -> Token:
        start_line, start_col = self.line, self.column
        chars = []
        while self._current().isalnum() or self._current() == "_":
            chars.append(self._advance())
        lexeme = "".join(chars)
        if lexeme in KEYWORDS:
            tok_type = "KEYWORD"
        elif lexeme in BOOL_LITERALS:
            tok_type = "BOOL_LITERAL"
        else:
            tok_type = "IDENTIFIER"
        return Token(tok_type, lexeme, start_line, start_col)

    def _scan_number(self) -> Token:
        start_line, start_col = self.line, self.column
        chars = []
        dot_count = 0
        while self._current().isdigit() or self._current() == ".":
            if self._current() == ".":
                dot_count += 1
                if not self._peek().isdigit() and dot_count == 1:
                    # Trailing dot like '5.' -> error
                    chars.append(self._advance())
                    self.errors.append(
                        CompilerError(
                            error_type="LexicalError",
                            message=f"Malformed float literal '{''.join(chars)}'.",
                            line=start_line,
                            column=start_col,
                            suggestion="Add digits after the decimal point, e.g., '5.0'.",
                        )
                    )
                    return Token("FLOAT_LITERAL", "".join(chars), start_line, start_col)
            chars.append(self._advance())

        lexeme = "".join(chars)
        if dot_count > 1:
            self.errors.append(
                CompilerError(
                    error_type="LexicalError",
                    message=f"Invalid numeric literal '{lexeme}' with multiple decimal points.",
                    line=start_line,
                    column=start_col,
                    suggestion="Use at most one decimal point in a numeric literal.",
                )
            )
            return Token("FLOAT_LITERAL", lexeme, start_line, start_col)

        tok_type = "FLOAT_LITERAL" if dot_count == 1 else "INT_LITERAL"
        return Token(tok_type, lexeme, start_line, start_col)

    def _scan_string(self) -> Token:
        start_line, start_col = self.line, self.column
        self._advance()  # opening quote
        chars = []
        closed = False
        while self.pos < len(self.source):
            ch = self._current()
            if ch == '"':
                self._advance()
                closed = True
                break
            if ch == "\n":
                break
            if ch == "\\" and self._peek() in ('"', "\\", "n", "t"):
                self._advance()
                esc = self._advance()
                mapping = {'"': '"', "\\": "\\", "n": "\n", "t": "\t"}
                chars.append(mapping.get(esc, esc))
            else:
                chars.append(self._advance())

        lexeme = "".join(chars)
        if not closed:
            self.errors.append(
                CompilerError(
                    error_type="LexicalError",
                    message="Unterminated string literal.",
                    line=start_line,
                    column=start_col,
                    suggestion='Close the string literal with a matching double quote (").',
                )
            )
        return Token("STRING_LITERAL", lexeme, start_line, start_col)

    def tokenize(self) -> Tuple[List[Token], List[CompilerError]]:
        self.tokens = []
        self.errors = []
        self.pos = 0
        self.line = 1
        self.column = 1

        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break

            ch = self._current()
            start_line, start_col = self.line, self.column

            if ch.isalpha() or ch == "_":
                self.tokens.append(self._scan_identifier_or_keyword())
            elif ch.isdigit():
                self.tokens.append(self._scan_number())
            elif ch == '"':
                self.tokens.append(self._scan_string())
            elif ch + self._peek() in TWO_CHAR_OPERATORS:
                op = self._advance() + self._advance()
                self.tokens.append(Token("OPERATOR", op, start_line, start_col))
            elif ch in SINGLE_CHAR_OPERATORS:
                op = self._advance()
                self.tokens.append(Token("OPERATOR", op, start_line, start_col))
            elif ch in DELIMITERS:
                delim = self._advance()
                self.tokens.append(Token("DELIMITER", delim, start_line, start_col))
            else:
                bad = self._advance()
                suggestion = "Remove or replace the invalid character."
                if bad == "&":
                    suggestion = "Did you mean logical AND '&&'?"
                elif bad == "|":
                    suggestion = "Did you mean logical OR '||'?"
                elif bad == "'":
                    suggestion = 'Use double quotes (") for string literals.'
                self.errors.append(
                    CompilerError(
                        error_type="LexicalError",
                        message=f"Unexpected character '{bad}'.",
                        line=start_line,
                        column=start_col,
                        suggestion=suggestion,
                    )
                )

        self.tokens.append(Token("EOF", "$", self.line, self.column))
        return self.tokens, self.errors
