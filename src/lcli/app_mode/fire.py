import sys

import fire

from lcli.app_mode.base import AppModeBase, AppModeException
from lcli.command.wrappers import ManualWrapper
from lcli.config import CommandCollection, ConfigException
from lcli.exceptions import BuilderException


class FireException(AppModeException):
    pass


class Fire(AppModeBase):
    from lcli.app import App

    def __init__(self, app: App):
        AppModeBase.__init__(self, app)
        self._command_alias_performed = False

    def run(self) -> None:
        """
        Run application in fire mode, that means it is not interactive
        See the specs of fire project
        :return:
        """
        args = self._app.get_args()
        command_path_index = 0
        for part in args:
            if part == "-":
                break
            command_path_index += 1
        remaining_args = args[command_path_index + 1 :]
        path = args[1:command_path_index]
        new_args = args[:command_path_index]
        if len(remaining_args):
            new_args.append('--args="' + " ".join(remaining_args) + '"')

        if len(new_args) >= 2:
            if self._app.get_app_code() == new_args[1]:
                temp_args = new_args[:1]
                if len(new_args) >= 3:
                    temp_args += new_args[2:]
                new_args = temp_args
                self._command_alias_performed = True

        sys.argv.clear()
        for arg in new_args:
            sys.argv.append(arg)

        self.fire_expose(path)

    def fire_expose(self, path: list) -> None:
        """
        Expose to fire a limited number of commands from provided config
        Depending on selected path from commands hierarchy

        :param path:
        :return:
        """

        executable_name = ""
        if len(path) > 0:
            executable_name = path[:1].pop()
        if executable_name == "--" or executable_name == "":
            executable_name = self._app.get_app_code()

        result_commands = self.get_available_commands(path)
        if self._command_alias_performed:
            if (
                len(result_commands) == 1
                and (
                    type(result_commands) is dict
                    or type(result_commands) is ManualWrapper
                )
                and executable_name in result_commands
            ):
                if (
                    type(result_commands[executable_name]) is dict
                    or type(result_commands[executable_name]) is ManualWrapper
                ):
                    temp_result = ManualWrapper()
                    temp_result.__doc__ = self._app.get_app_description()

                    for key in result_commands[executable_name]:
                        temp_result[key] = result_commands[executable_name][key]
                    result_commands = temp_result

        fire.Fire(result_commands, None, executable_name)

    def get_available_commands(self, path: list) -> ManualWrapper:
        """
        Return the available commands in a given path in order to load just a potion of configs in Fire mode
        :param path:
        :return:
        """
        try:
            if len(path) > 0:
                command = path[:1].pop()
                if command == "--":
                    path = []

            if not len(path):
                command_collection = self._app.get_commands()
            else:
                try:
                    command_collection = CommandCollection({})
                    command_found = self._app.get_commands().get_command_by_path(
                        path=path[:1], return_first_executable=True
                    )
                    command_collection.add_command(command_found)
                except Exception:
                    command_collection = self._app.get_commands()
        except ConfigException as e:
            command_collection = CommandCollection({})
            self._app.logger.error(e)

        return self.build_commands_object_recursively(command_collection)

    def build_commands_object_recursively(
        self, commands_list: CommandCollection
    ) -> ManualWrapper:
        """
        Build command objects or references prepared to Fire from a CommandCollection object recursively
        It is needed because for now it rely on Fire documentation and the object should be prepared and ready to execute

        :param commands_list:
        :return: dict containing instances of objects in a hierarchy manner
        """
        config_object = self._app.get_config_object()

        command_builder_factory = self._app.get_command_builder_factory()
        result_commands = ManualWrapper()
        for key in commands_list:
            try:
                command = commands_list.get_command(key)
                if command.is_group():
                    if not config_object.is_command_group_available(key):
                        continue
                    group_objects = self.build_commands_object_recursively(
                        command.commands
                    )
                    if type(group_objects) is ManualWrapper:
                        group_objects.__doc__ = command.description

                    if key == "groups":
                        result_commands.__update__(group_objects)
                    else:
                        result_commands[key] = group_objects
                else:
                    if not config_object.is_command_available(key):
                        continue
                    result_commands[key] = command_builder_factory.create(
                        command
                    ).build(command)
            except BuilderException as e:
                self._app.logger.warning(e)

        return result_commands
