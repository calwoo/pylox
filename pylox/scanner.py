from pylox.token_type import TokenType
from pylox.token import Token
from pylox.error import error


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []

        # position in scanner
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end:
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line)
        )
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()
        # single-character tokens
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        # one or two character tokens
        elif c == "!":
            potential_next = TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
            self.add_token(potential_next)
        elif c == "=":
            potential_next = TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            self.add_token(potential_next)
        elif c == "<":
            potential_next = TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
            self.add_token(potential_next)
        elif c == ">":
            potential_next = TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            self.add_token(potential_next)
        # division is tricky (could be a comment)
        elif c == "/":
            if self.match("/"):
                # is a comment, advance til next line
                while self.peek() != "\n" and not self.is_at_end:
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        # newlines
        elif c == "\n":
            self.line += 1
        else:
            error(self.line, "Unexpected character.")

    def match(self, expected: str) -> bool:
        if self.is_at_end:
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end:
            return "\0"
        return self.source[self.current]
    
    @property
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type: TokenType, literal: object = None):
        text: str = self.source[self.start: self.current]
        self.tokens.append(
            Token(type, text, literal, self.line)
        )
