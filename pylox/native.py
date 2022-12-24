import time

from pylox.callable import LoxCallable


class Clock(LoxCallable):
    def call(self, interpreter, arguments: list[object]) -> object:
        return time.process_time()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<clock:native fn>"
