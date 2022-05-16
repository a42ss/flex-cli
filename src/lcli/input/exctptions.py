class InputException(Exception):
    pass


class InterruptedInputException(InputException):
    def __init__(self, message: str, partial_answers: dict, errors=None):
        if errors is None:
            errors = []
        self.errors = errors
        self.partial_answers = partial_answers
        self.message = message
        super().__init__(self.message)
