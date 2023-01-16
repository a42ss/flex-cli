from typing import Callable, Optional

from ..api.application import ApplicationResultInterface


class CliResponse(ApplicationResultInterface):
    _content: str | None = None
    _exit_code: int = 0

    class Const:
        EXIT_CODE_SUCCESS: int = 0

    class Factory:
        @staticmethod
        def create(exit_code, content: Optional[str] = None):
            return CliResponse(exit_code, content)

    def __init__(self, exit_code: int = 0, content: Optional[str] = None):
        self._content = content
        self._exit_code = exit_code

    def send_response(self, after_execute_callback: Optional[Callable] = None):
        if self._content is not None and len(self._content):
            print(self._content)

        if after_execute_callback is not None:
            after_execute_callback()
        exit(self._exit_code)
