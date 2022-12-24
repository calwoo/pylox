from pylox.token import Token
from pylox.error import LoxRuntimeError


class Environment:
    """
    Variable binding environment. Implements lexical scoping through enclosing blocks.
    """

    def __init__(self):
        self.blocks: list[dict[str, object]] = [{}]
        self.innermost = 0

    def in_block(self):
        self.blocks.append({})
        self.innermost += 1

    def out_block(self):
        self.blocks.pop()
        self.innermost -= 1

    @property
    def n_blocks(self):
        return self.innermost + 1

    def define(self, name: str, value: object):
        inner_env = self.blocks[self.innermost]
        inner_env[name] = value

    def get(self, name: Token) -> object:
        env_idx = self.innermost
        while env_idx >= 0:
            env = self.blocks[env_idx]
            if name.lexeme in env:
                return env[name.lexeme]
            env_idx -= 1
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}.")

    def assign(self, name: Token, value: object):
        # search envs for innermost definition of name, but assign value in innermost block env
        # check variable
        var_found: bool = False
        for env in self.blocks:
            if name.lexeme in env:
                var_found = True
                break

        if var_found:
            inner_env = self.blocks[self.innermost]
            inner_env[name.lexeme] = value
            return
        
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")