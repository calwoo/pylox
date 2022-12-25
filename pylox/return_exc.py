from pylox.error import LoxRuntimeError


class ReturnException(LoxRuntimeError):
    def __init__(self, value: object):
        self.value = value
        super().__init__(None, None)
