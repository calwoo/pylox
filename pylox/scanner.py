from pylox.token_type import TokenType
from pylox.token import Token
from pylox.error import error


keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


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
        # newlines and whitespace
        elif c.isspace():
            pass
        elif c == "\n":
            self.line += 1
        # string literals
        elif c == '"':
            self.string()
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                # identifiers and keywords
                self.identifier()
            else:
                error(self.line, "Unexpected character.")

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end:
            if self.peek() == "\n":
                # allows for multi-line strings
                self.line += 1
            self.advance()

        if self.is_at_end:
            error(self.line, "Unterminated string.")
            return

        # closing "
        self.advance()

        value: str = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        value: str = self.source[self.start: self.current]
        self.add_token(TokenType.NUMBER, float(value))

    def identifier(self) -> None:
        while self.is_alphanumeric(self.peek()):
            self.advance()
        
        text: str = self.source[self.start: self.current]
        type: TokenType = keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

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

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def is_digit(self, c: str) -> bool:
        return c.isnumeric()

    def is_alpha(self, c: str) -> bool:
        return c.isalpha()

    def is_alphanumeric(self, c: str) -> bool:
        return self.is_digit(c) or self.is_alpha(c)
    
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
