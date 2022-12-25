from abc import ABC, abstractmethod
from typing import Optional

from pylox.token import Token


# visitors
class ExprVisitor(ABC):
    @abstractmethod
    def visit_literal_expr(self, expr):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr):
        pass

    @abstractmethod
    def visit_assign_expr(self, expr):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr):
        pass

    @abstractmethod
    def visit_call_expr(self, expr):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr):
        pass


class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt):
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt):
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt):
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt):
        pass


# expressions
class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor):
        pass


class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    def __init__(
        self,
        left: Expr,
        operator: Token,
        right: Expr,
    ):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_logical_expr(self)


class Grouping(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping_expr(self)


class Unary(Expr):
    def __init__(
        self,
        operator: Token,
        right: Expr,
    ):
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary_expr(self)


class Assign(Expr):
    def __init__(
        self,
        name: Token,
        value: Expr,
    ):
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(
        self, 
        left: Expr, 
        operator: Token, 
        right: Expr
    ):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary_expr(self)


class Call(Expr):
    def __init__(
        self,
        callee: Expr,
        paren: Token,
        arguments: list[Expr],
    ):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_call_expr(self)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_variable_expr(self)


# statements
class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        pass


class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block_stmt(self)


class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)


class Function(Stmt):
    def __init__(
        self,
        name: Token,
        params: list[Token],
        body: list[Stmt],
    ):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_function_stmt(self)


class If(Stmt):
    def __init__(
        self,
        condition: Expr,
        then_branch: Stmt,
        else_branch: Optional[Stmt],
    ):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)


class While(Stmt):
    def __init__(
        self,
        condition: Expr,
        loop_body: Stmt,
    ):
        self.condition = condition
        self.loop_body = loop_body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_stmt(self)

    
class Print(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)
