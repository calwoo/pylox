from abc import ABC, abstractmethod
from pylox.token import Token


# visitors
class ExprVisitor(ABC):
    @abstractmethod
    def visit_literal_expr(self, expr):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr):
        pass


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt):
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


class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)

    
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
