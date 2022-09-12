from lcli.app import App
from lcli.command.builders import BaseBuilder
from lcli.command.input import ParametersReader
from lcli.command.subprocess import CommandRunner
from lcli.config import Command
from lcli.tools.base import BaseTool


class BaseCommandWrapperInterface(object):
    pass


class BashCommandWrapperInterface(BaseCommandWrapperInterface):
    pass


class BashCommandWrapper(BaseTool, BashCommandWrapperInterface):
    """
    Run command from configuration, commands with type wrapper
    This will consist of executing shell commands on a given directory using configuration, parameters completion and
    interactive selections of parameters
    """

    _command_name: str
    _command: Command

    def __init__(self, app: App, command: Command) -> None:
        super().__init__(app)
        self._command_name = command.name
        self._command = command
        self.__init_command()

    def __init_command(self):
        self.__doc__ = self._command.description

        sub_commands = self._command.commands
        for command_code in sub_commands:
            current_command = sub_commands[command_code]
            current_command_obj = CommandRunner(
                current_command,
                self._app.get_config_object().get(
                    ["commands_defaults", self._command_name], default={}
                ),
                self._app.get_object_manager().provide(ParametersReader.Factory),
                self._command,
            )
            current_command_obj.__doc__ = (
                current_command.description + " (" + current_command.args.command + ")"
            )
            setattr(self, command_code, current_command_obj)

    class _Builder(BaseBuilder):
        """
        This will be a custom builder for current wrapper, custom ones may be implemented
        """

        def build(self, command: Command) -> "BashCommandWrapper":
            return BashCommandWrapper(self._app, command)


class ManualWrapper:
    def __init__(self):
        self._dict = {}

    def __iter__(self):
        return self._dict.__iter__()

    def __setitem__(self, name, value):
        setattr(self, name, value)
        self._dict[name] = value

    def __getitem__(self, name):
        return self._dict[name]

    def __contains__(self, key):
        return key in self._dict

    def __update__(self, value):
        self._dict = value

    def __len__(self):
        return len(self._dict)
