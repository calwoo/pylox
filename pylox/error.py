import sys


had_error: bool = False

# basic error handlers
def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    global had_error # ugh, globals!
    print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
    had_error = True
