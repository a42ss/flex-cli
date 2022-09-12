from pydoc import locate
from typing import Dict, List

from lcli.app import App
from lcli.config import Command
from lcli.exceptions import BuilderException


class BaseBuilder:
    """
    Build various type of objects to use them in Fire application mode
    Mandatory to define the command_type for each builder
    """

    _app: App
    command_type: str = "n/a"

    def __init__(self, app: App) -> None:
        self._app = app

    def can_build(self, command: Command) -> bool:
        return command.type == self.command_type

    def build(self, command: Command):
        raise BuilderException("Command builder not implemented for: " + command.name)

    @classmethod
    def locate(cls, path: str):
        try:
            return locate(path)
        except Exception:
            raise BuilderException(
                "Invalid configuration provided for command. Path "
                + path
                + " could not be loaded."
            )


class CommandBuilderFactory(object):
    """
    Create instances of builders responsible to construct objects for fire application mode
    """

    _app: App
    _builders_available: List[BaseBuilder] = []
    _builders_instances_cache: Dict[str, BaseBuilder] = {}

    def __init__(self, app: App) -> None:
        self._app = app

    @staticmethod
    def register_builder(class_ref):
        """
        Register your custom builder for command type, this should be called before first usage

        :param class_ref:
        :return:
        """
        CommandBuilderFactory._builders_available.append(class_ref)
        return CommandBuilderFactory

    def create(self, command: Command) -> BaseBuilder:
        """
        Create the first builder that can construct the command object for current command

        :param command:
        :return:
        """
        for builder in self._builders_available:
            builder_object = self.get_builder(builder)
            if builder_object.can_build(command):
                return builder_object
        raise BuilderException(
            "Unable to find a proper command builder for command: " + command.name
        )

    def get_builder(self, builder) -> BaseBuilder:
        """
        Return builder object by class, and keep cache of instantiated objects

        :param builder:
        :return:
        """
        if builder.command_type not in self._builders_instances_cache:
            self._builders_instances_cache[builder.command_type] = builder(self._app)
        return self._builders_instances_cache[builder.command_type]


class LcliBuilder(BaseBuilder):
    """
    This builder is responsible to construct objects located in lcli.tools namespace
    Usually extended form lcli.tools.Base.BaseTool
    """

    command_type: str = Command.Constants.TYPES.LCLI

    def build(self, command: Command):
        located_object = locate(command.args.command)
        if callable(located_object):
            return located_object(self._app)


class SimpleBuilder(BaseBuilder):
    """
    A simple command object, without other dependencies
    """

    command_type: str = Command.Constants.TYPES.FUNCTION

    def canBuild(self, command: Command) -> bool:
        if command.type is None:
            return True
        return super().can_build(command)

    def build(self, command: Command):
        return locate(command.args.command)


class WrappersBuilder(BaseBuilder):
    """
    This will build a "virtual" command object capable to execute commands form configuration
    """

    command_type: str = Command.Constants.TYPES.WRAPPER

    def build(self, command: Command):
        try:
            wrappers = self._app.get_commands_wrappers()
            wrapper_object = wrappers.get(command.args.get("wrapper"))
            builder_name = wrapper_object.get("builder")
            if (
                builder_name is not None
                and type(builder_name) == str
                and len(builder_name)
            ):
                builder = locate(builder_name)
                if callable(builder):
                    builder_object = builder(self._app)
                    if callable(builder_object):
                        return builder_object.build(command)

            handler = locate(wrapper_object.get("handler"))
            if callable(handler):
                return handler(self._app, command)

        except Exception as e:
            self._app.logger.warning(e)
            raise BuilderException("Unable to build command: " + command.name)
