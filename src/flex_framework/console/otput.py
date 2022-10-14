from typing import Callable

from ..api.application import ApplicationResultInterface


class CliResponse(ApplicationResultInterface):
    _content: str = None
    _exit_code: int = 0

    class Const:
        EXIT_CODE_SUCCESS: int = 0

    class Factory:
        @staticmethod
        def create(exit_code, content: str = None):
            return CliResponse(exit_code, content)

    def __init__(self, exit_code: 0, content: str = None):
        self._content = content
        self._exit_code = exit_code

    def send_response(self, after_execute_callback: Callable = None):
        if self._content is not None and len(self._content):
            print(self._content)

        if after_execute_callback is not None:
            after_execute_callback()
        exit(self._exit_code)
