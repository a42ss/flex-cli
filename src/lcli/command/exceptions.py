from lcli.config import CommandParam


class CommandException(Exception):
    pass


class RequiredParameterException(CommandException):
    def __init__(self, parameter: CommandParam):
        self.parameter = parameter
