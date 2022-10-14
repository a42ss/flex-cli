from abc import ABC, abstractmethod

from ..console.otput import CliResponse
from . import get_class_path as get_handler


class HandlerInterface(ABC):
    class Const:
        HANDLERS = "handlers"
        DEFAULT_HANDLER: str = "default_handler"

    @abstractmethod
    def handle(self) -> CliResponse:
        pass
