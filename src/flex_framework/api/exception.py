class FlexExceptionInterface(Exception):
    message: str
    error_code: int = 0
    exit_code: int = 0

    def __init__(self, *args: object):
        super().__init__(args)
        self.message = str(args[0])

    def get_code(self) -> int:
        return self.error_code

    def get_exit_code(self) -> int:
        return self.exit_code

    def get_message(self) -> str:
        return self.message
