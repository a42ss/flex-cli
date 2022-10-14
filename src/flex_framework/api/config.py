from abc import ABC, abstractmethod


class ConfigInterface(ABC):
    @abstractmethod
    def get(self):
        pass
