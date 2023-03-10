from pylox.token_type import TokenType


class Token:
    """
    Container class for a token for parsing.
    """

    def __init__(
        self,
        type: TokenType,
        lexeme: str,
        literal: object,
        line: int
    ):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal}"
