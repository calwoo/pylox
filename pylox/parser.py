from typing import Optional

from pylox.token_type import TokenType
from pylox.token import Token
from pylox.error import report
from pylox.expr import *


class Parser:
    """
    Recursive descent parser.
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current: int = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._is_at_end:
            statements.append(self.declaration())

        return statements

    def declaration(self) -> Stmt:
        try:
            if self._match(TokenType.VAR):
                return self.variable_declaration()
            return self.statement()
        except Exception:
            self._synchronize()
            return None

    def statement(self) -> Stmt:
        if self._match(TokenType.PRINT):
            return self.print_stmt()
        return self.expr_stmt()

    def print_stmt(self) -> Stmt:
        value: Expr = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def variable_declaration(self) -> Stmt:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr = None
        if self._match(TokenType.EQUAL):
            # optional initializer in lox language
            initializer = self.expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return Var(name, initializer)

    def expr_stmt(self) -> Stmt:
        expr: Expr = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr: Expr = self.comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            operator: Token = self._previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self.unary()
            expr = Unary(operator, right)
        else:
            expr = self.primary()
        return expr

    def primary(self) -> Expr:
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        elif self._match(TokenType.TRUE):
            return Literal(True)
        elif self._match(TokenType.FALSE):
            return Literal(False)
        elif self._match(TokenType.NIL):
            return Literal(None)
        elif self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())
        elif self._match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        self._error(self._peek(), "Expect expression.")

    def _match(self, *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _check(self, type: TokenType) -> bool:
        if self._is_at_end:
            return False
        return self._peek().type == type

    def _advance(self) -> None:
        if not self._is_at_end:
            self.current += 1
        return self._previous()

    @property
    def _is_at_end(self):
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _consume(self, type: TokenType, error_msg: str) -> None:
        if self._check(type):
            return self._advance()
        raise self._error(self._peek(), error_msg)

    def _error(self, token: Token, error_msg: str) -> Exception:
        if token.type == TokenType.EOF:
            report(token.line, " at end", error_msg)
        else:
            report(token.line, f" at {token.lexeme}", error_msg)
        return Exception(error_msg)

    def _synchronize(self) -> None:
        self._advance()

        while not self._is_at_end:
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            return_types = [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]

            if self._peek().type in return_types:
                return

            self._advance()
