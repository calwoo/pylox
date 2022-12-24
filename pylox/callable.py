from abc import ABC, abstractmethod


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: list[object]) -> object:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass
