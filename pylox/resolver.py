from typing import Union

from pylox.expr import *
from pylox.token import Token
from pylox.token_type import TokenType
from pylox.error import report


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._resolve(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt)

    def visit_if_stmt(self, stmt: If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self._resolve(stmt.expression)
    
    def visit_return_stmt(self, stmt: Return) -> None:
        if stmt.value is not None:
            self._resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_while_stmt(self, stmt: While) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_assign_expr(self, expr: Assign) -> None:
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Binary) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        self._resolve(expr.callee)
        for argument in expr.arguments:
            self._resolve(argument)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self._resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> None:
        return

    def visit_unary_expr(self, expr: Unary):
        self._resolve(expr.right)

    def visit_variable_expr(self, expr: Variable) -> None:
        if (len(self.scopes) == 0) and not self.scopes[-1].get(expr.name.lexeme):
            self._error(expr.name, "Can't read local variable in its own initializer.")

        self._resolve_local(expr, expr.name)

    def _resolve(self, statements: Union[Expr, Stmt, list[Stmt]]) -> None:
        if isinstance(statements, list):
            for statement in statements:
                self._resolve(statement)
        
        statements.accept(self)

    def _resolve_function(self, function: Function) -> None:
        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        
        self._resolve(function.body)
        self._end_scope()

    def _begin_scope(self) -> None:
        self.scopes.append({})

    def _end_scope(self) -> None:
        self.scopes.pop()

    def _declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        
        scope: dict[str, bool] = self.scopes[-1]
        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return

        scope: dict[str, bool] = self.scopes[-1]
        scope[name.lexeme] = True

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        for dist, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, dist)
                return

    def _error(self, token: Token, error_msg: str) -> Exception:
        if token.type == TokenType.EOF:
            report(token.line, " at end", error_msg)
        else:
            report(token.line, f" at {token.lexeme}", error_msg)
        return Exception(error_msg)
