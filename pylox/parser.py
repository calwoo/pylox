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
            if self._match(TokenType.FUN):
                return self.function("function")
            return self.statement()
        except Exception:
            self._synchronize()
            return None

    def statement(self) -> Stmt:
        if self._match(TokenType.IF):
            return self.if_stmt()
        if self._match(TokenType.WHILE):
            return self.while_stmt()
        if self._match(TokenType.FOR):
            return self.for_stmt()
        if self._match(TokenType.PRINT):
            return self.print_stmt()
        if self._match(TokenType.RETURN):
            return self.return_stmt()
        if self._match(TokenType.LEFT_BRACE):
            block = Block(self.block())
            return block
        return self.expr_stmt()

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while (not self._check(TokenType.RIGHT_BRACE)) and (not self._is_at_end):
            statements.append(self.declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def function(self, kind: str) -> Stmt:
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                
                parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body: list[Stmt] = self.block()
        return Function(name, parameters, body)

    def if_stmt(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self.statement()
        else_branch: Optional[Stmt] = None
        if self._match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def while_stmt(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body: Stmt = self.statement()
        return While(condition, body)

    def for_stmt(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        # parse initializer
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expr_stmt()

        # parse condition
        condition: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        # parse increment
        increment: Optional[Expr] = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        loop_body: Stmt = self.statement()
        # desugar for into while
        if increment is not None:
            loop_body = Block(
                [
                    loop_body,
                    Expression(increment),
                ]
            )

        if condition is None:
            condition = Literal(True)
        loop_body = While(condition, loop_body)

        if initializer is not None:
            loop_body = Block(
                [
                    initializer,
                    loop_body
                ]
            )

        return loop_body

    def print_stmt(self) -> Stmt:
        value: Expr = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def return_stmt(self) -> Stmt:
        keyword: Token = self._previous()
        value: Expr = None
        if not self._check(TokenType.SEMICOLON):
            value = self.expression()
        
        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

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
        return self.assignment()

    def assignment(self) -> Expr:
        # expr: Expr = self.equality()
        expr: Expr = self.logical_or()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self.assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            self._error(equals, "Invalid assignment target.")
        return expr

    def logical_or(self) -> Expr:
        expr: Expr = self.logical_and()
        
        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self.logical_and()
            expr = Logical(expr, operator, right)

        return expr

    def logical_and(self) -> Expr:
        expr: Expr = self.equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)

        return expr

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
            expr = self.call()
        return expr

    def call(self) -> Expr:
        callee_expr: Expr = self.primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                callee_expr = self.finish_call(callee_expr)
            else:
                break

        return callee_expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self._match(TokenType.COMMA):
                    break

        paren: Token = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)


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
            variable = Variable(self._previous())
            return variable
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

    def _advance(self) -> Token:
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

    def _consume(self, type: TokenType, error_msg: str) -> Token:
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
