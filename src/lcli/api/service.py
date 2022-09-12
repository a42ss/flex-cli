from abc import abstractmethod


class ServiceInterface:
    @abstractmethod
    def do_something(self):
        pass
