from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..application import ApplicationBootstrap


T = TypeVar("T")


class ApplicationResultInterface(ABC):
    pass


class ApplicationInterface(Generic[T], ABC):
    class Const:
        pass

    @abstractmethod
    def launch(self) -> T:
        pass

    def terminate(self, exception: Exception):
        print("Unhandled exception: " + str(exception))
        exit(1)

    def catch_exception(self, bootstrap: ApplicationBootstrap, exception: Exception):
        raise exception
