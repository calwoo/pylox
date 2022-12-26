from pylox.expr import *
from pylox.environment import Environment
from pylox.callable import LoxCallable
from pylox.function import LoxFunction
from pylox.error import LoxRuntimeError, report_runtime_error
from pylox.return_exc import ReturnException
from pylox.token_type import TokenType
from pylox.native import Clock


class Interpreter(ExprVisitor, StmtVisitor):
    environment: Environment = Environment()

    def interpret(self, statements: list[Stmt]) -> None:
        # add in natives
        self.environment.globals["clock"] = Clock()

        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeError as e:
            report_runtime_error(e)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> object:
        left: object = self._evaluate(expr.left)
        
        # short circuit if possible
        if self._is_truthy(left) and (expr.operator.type == TokenType.OR):
            return left
        elif (not self._is_truthy(left)) and (expr.operator.type == TokenType.AND):
            return False
        else:
            return self._evaluate(expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expr)

    def visit_unary_expr(self, expr: Unary) -> object:
        right: object = self._evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not self._is_truthy(right)
        
        # unreachable!
        return None

    def visit_variable_expr(self, expr: Var) -> object:
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign) -> object:
        value: object = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> object:
        left: object = self._evaluate(expr.left)
        right: object = self._evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return float(left) - float(right)
        elif expr.operator.type == TokenType.PLUS:
            # for numbers, this is addition
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            # for strings, concatenate
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        elif expr.operator.type == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)

        # unreachable!
        return None

    def visit_call_expr(self, expr: Call) -> object:
        callee = self._evaluate(expr.callee)
        arguments: list[object] = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._execute_block(stmt.statements)

    def visit_if_stmt(self, stmt: If) -> None:
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: While) -> None:
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.loop_body)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_print_stmt(self, stmt: Print) -> None:
        value: object = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_return_stmt(self, stmt: Return) -> None:
        value: object = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)
        
        # throw an exception to escape the call stack
        raise ReturnException(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value: object = None
        if not stmt.initializer is None:
            value = self._evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def _execute_block(self, statements: list[Stmt]):
        self.environment.in_block()
        try:
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment.out_block()

    def _evaluate(self, expr: Expr) -> object:
        # self-reflection
        return expr.accept(self)

    def _is_truthy(self, obj: object) -> bool:
        # ruby semantics: false and nil are falsey, everything else is truthy!
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def _is_equal(self, x: object, y: object) -> bool:
        return x == y

    def _stringify(self, value: object) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float):
            text: str = str(value)
            if text.endswith(".0"):
                text = str(int(float(text)))
            return text
        return str(value)
        
    def _check_number_operand(self, operator: Token, operand: object) -> None:
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: object, right: object) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")
