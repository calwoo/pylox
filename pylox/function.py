from pylox.callable import LoxCallable
from pylox.environment import Environment
from pylox.return_exc import ReturnException


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments: list[object]) -> object:
        self.closure.in_block()
        for arg, val in zip(self.declaration.params, arguments):
            self.closure.define(arg.lexeme, val)

        # shadow interpreter environment
        original_env = interpreter.environment
        interpreter.environment = self.closure

        value: object = None
        try:
            interpreter._execute_block(self.declaration.body)
        except ReturnException as e:
            value = e.value
        finally:
            # restore original environment
            interpreter.environment = original_env

        return value

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
