from abc import abstractmethod

from lcli.config import CommandParam


class CommandInterface:
    @abstractmethod
    def do_something(self):
        pass


class CommandRunnerInterface:
    @abstractmethod
    def do_something(self):
        pass


class CommandWrapperInterface:
    pass


class CommandBuilderInterface:
    pass


class CommandBuilderFactoryInterface:
    pass


class CommandException(Exception):
    pass


class RequiredParameterException(CommandException):
    def __init__(self, parameter: CommandParam):
        self.parameter = parameter
