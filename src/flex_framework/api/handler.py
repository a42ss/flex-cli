from abc import ABC, abstractmethod

from ..console.otput import CliResponse
from . import get_class_path


def get_handler(class_reference):
    return get_class_path(class_reference)


class HandlerInterface(ABC):
    class Const:
        HANDLERS = "handlers"
        DEFAULT_HANDLER: str = "default_handler"

    @abstractmethod
    def handle(self) -> CliResponse:
        pass
