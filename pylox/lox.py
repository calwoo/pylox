import os
import sys
import argparse

from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.interpreter import Interpreter
from pylox.error import *


def main() -> None:
    """
    Main entrypoint for pylox interpreter.
    """

    parser = argparse.ArgumentParser(
        usage="pylox [SCRIPT]",
        description="Interpreter for the lox programming language."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version="0.1.0",
    )
    parser.add_argument("script", nargs='*')
    args = parser.parse_args()
    
    if len(args.script) > 1:
        raise ValueError("Usage: pylox [script]")
    elif len(args.script) == 1:
        run_file(args.script[0])
    else:
        run_prompt()


def run_file(path: str) -> None:
    """
    Reads lox script and runs it.
    """

    if not os.path.exists(path):
        raise FileNotFoundError("lox script not found!")
    
    with open(path, "r") as f:
        script = f.read()
    run(script)

    if had_error:
        sys.exit(65)

    if had_runtime_error:
        sys.exit(70)


def run_prompt() -> None:
    """
    Open interactive REPL.
    """

    global had_error

    while True:
        try:
            print("> ", end="")
            line = input()
            if line == "":
                continue
            run(line)
            had_error = False
        except EOFError:
            break


def run(script: str) -> None:
    global had_error

    scanner = Scanner(script)
    tokens = scanner.scan_tokens()

    # for token in tokens:
    #     print(token)

    parser = Parser(tokens)
    statements = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(statements)


if __name__ == "__main__":
    main()
