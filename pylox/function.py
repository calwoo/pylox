from pylox.callable import LoxCallable
from pylox.environment import Environment
from pylox.return_exc import ReturnException


class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration

    def call(self, interpreter, arguments: list[object]) -> object:
        global_env = interpreter.environment.globals
        environment: Environment = Environment(global_env=global_env)

        environment.in_block()
        for arg, val in zip(self.declaration.params, arguments):
            environment.define(arg.lexeme, val)

        # shadow interpreter environment
        original_env = interpreter.environment
        interpreter.environment = environment

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
