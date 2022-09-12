from abc import abstractmethod


class ControllerInterface:
    @abstractmethod
    def run(self) -> None:
        pass
