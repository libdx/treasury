_TREASURE_NOT_DEFINED_ERROR = "Treasure not defined."

_SUCCESSFUL_ATTEMPT_EXISTS = "Successful attempt already exists"


class TreasureNotDefinedError(Exception):
    def __init__(self, message=None):
        super().__init__(message or _TREASURE_NOT_DEFINED_ERROR)


class SuccessfulAttemptExistsError(Exception):
    def __init__(self, message=None):
        super().__init__(message or _SUCCESSFUL_ATTEMPT_EXISTS)
