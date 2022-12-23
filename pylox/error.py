import sys


had_error: bool = False
had_runtime_error: bool = False

# basic error handlers
def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    global had_error # ugh, globals!
    print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
    had_error = True


class LoxRuntimeError(Exception):
    def __init__(self, token, error_msg):
        self.token = token
        self.error_msg = error_msg
        super().__init__(self.error_msg)


def report_runtime_error(error):
    global had_runtime_error
    print(f"[line {error.token.line}] {error.error_msg}", file=sys.stderr)
    had_runtime_error = True
