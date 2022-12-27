from copy import deepcopy

from pylox.callable import LoxCallable
from pylox.environment import Environment
from pylox.return_exc import ReturnException


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure: Environment):
        self.declaration = declaration
        # create a deepcopy of environment
        self.closure = Environment()
        self.closure.blocks.pop()
        for block in closure.blocks:
            self.closure.blocks.append(deepcopy(block))
        self.closure.innermost = closure.innermost

    def call(self, interpreter, arguments: list[object]) -> object:
        closure = self._replicate_env(self.closure)
        closure.in_block()
        for arg, val in zip(self.declaration.params, arguments):
            closure.define(arg.lexeme, val)
        # shadow interpreter environment
        original_env = interpreter.environment
        interpreter.environment = closure

        value: object = None
        try:
            interpreter._execute_block(self.declaration.body, new_scope=False)
        except ReturnException as e:
            value = e.value
        finally:
            # restore original environment
            interpreter.environment = original_env
            closure.out_block()

        return value

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def _replicate_env(self, environment: Environment) -> Environment:
        replication: Environment = Environment()
        replication.blocks.pop()
        for block in environment.blocks:
            replication.blocks.append(deepcopy(block))
        replication.innermost = environment.innermost

        return replication
