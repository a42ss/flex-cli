import copy
import errno
import logging
import os
import sys

import pinject
from blessings import Terminal as Translator

from lcli.cache import Cache, CacheNotFoundException
from lcli.config import (
    CommandCollection,
    CommandsConfig,
    CommandWrapperCollection,
    Config,
    ConfigNamespaces,
    ConfigValidationError,
    YamlConfigReader,
)
from lcli.utils import setup_logger


class AppException(Exception):
    pass


class Output(object):
    @staticmethod
    def print(message: str, args: list):
        print(message.format(*args))

    @staticmethod
    def format(message: str, args: list):
        return message.format(*args)


class App:
    CACHE_LIFETIME = 86400
    _app_path: str
    _current_command: list[str] = []

    _object_manager: pinject.object_graph.ObjectGraph
    translator = __ = Translator()
    output = Output()
    logger: logging.Logger

    FLAG_INTERACTIVE = "-i"
    FLAG_VERBOSE = "-v"
    FLAG_DEBUG = "-d"

    _flags: dict[str, str] = {}
    _available_flags = [FLAG_INTERACTIVE, FLAG_VERBOSE, FLAG_DEBUG]

    _working_directory: str = ""
    _user_home_directory: str = ""
    _user_home_directory_path: str = ""

    CONF_EXECUTABLE_PATH: str = "cli_executable_path"
    CONF_EXECUTABLE_NAME: str = "cli_executable_name"
    _executable_path: str
    _executable_name: str

    _config_folder_defaults = "config"
    _config_folder_working_directory = ".lcli"
    _config_folder_defaults_path = ""
    _working_directory_conf_path: str = ""
    _config_folder_home_directory = os.path.join(".config", ".lcli")
    _config_namespace = "commands"
    _log_file = "lcli.log"
    _cache_directory_path: str

    _commands: CommandCollection
    _commands_wrappers: CommandWrapperCollection

    def __init__(
        self, app_path: str, cwd: str, executable_name: str, init_params: dict
    ):

        if "flags" in init_params:
            init_flags = init_params["flags"]
            if type(init_flags) == list:
                for flag in init_flags:
                    self._flags[flag] = flag

        self._working_directory = cwd
        self._user_home_directory = os.path.expanduser("~")
        self._working_directory_conf_path = os.path.join(
            self.get_working_directory(), self._config_folder_working_directory
        )
        self._config_folder_defaults_path = os.path.join(
            os.path.dirname(__file__), self._config_folder_defaults
        )
        self._user_home_directory_path = os.path.join(
            self._user_home_directory, self._config_folder_home_directory
        )
        self._cache_directory_path = os.path.join(
            self._user_home_directory_path, "cache"
        )
        self._config_folders = [
            self._config_folder_defaults_path,
            self._user_home_directory_path,
            self._working_directory_conf_path,
        ]

        self._config_object = CommandsConfig({})
        self._app_path = app_path
        self.init()
        self._executable_name = self._config_object.get(
            App.CONF_EXECUTABLE_NAME, executable_name
        )

    # <Init section
    def init(self):
        sys.path.append(self._working_directory_conf_path)
        sys.path.append(self._working_directory_conf_path)
        self.init_default_flags()
        self.init_logger()
        self.init_commands_configs()
        self._executable_path = self._config_object.get(App.CONF_EXECUTABLE_PATH, "")
        self.init_object_manager()

    def init_default_flags(self):
        to_remove_args = []
        for flag in sys.argv:
            if flag[0] == "-":
                if flag in self._available_flags:
                    self._flags[flag] = flag
                    to_remove_args.append(flag)
        for flag in to_remove_args:
            sys.argv.remove(flag)

        command_args = copy.deepcopy(sys.argv)
        command_args.pop(0)

        if len(command_args) > 0 and command_args[0] == "--":
            self._current_command = ""
        else:
            self._current_command = command_args

    def init_logger(self):
        import logging

        verb = logging.ERROR
        if self.is_verbose():
            verb = logging.INFO

        self.logger = setup_logger(
            "APP", verbosity=verb, file=self.get_log_file(self._log_file)
        )

    def init_commands_configs(self):
        config_object = self.construct_config_object(
            ConfigNamespaces.COMMANDS,
            self.get_config_files_by_namespace(ConfigNamespaces.COMMANDS),
            os.path.join(self._config_folder_defaults_path, "schema", "commands.json"),
        )
        self._config_object = CommandsConfig(config_object.get_all())
        self._commands = CommandCollection(self._config_object.get_commands())
        self._commands_wrappers = CommandWrapperCollection(
            self._config_object.get_commands_wrappers()
        )

    def get_config_files_by_namespace(self, namespace: str) -> list:
        config_files = []
        for folder in self._config_folders:
            if len(self._current_command) > 0:
                config_files.append(
                    os.path.join(folder, namespace, self._current_command[0] + ".yml")
                )
            else:
                for other_file in self.discover_configuration_file(
                    os.path.join(folder, namespace)
                ):
                    config_files.append(other_file)

            config_files.append(os.path.join(folder, namespace + ".yml"))

        return config_files

    @classmethod
    def discover_configuration_file(cls, directory: str):
        result = []
        if os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".yml"):
                        result.append(os.path.join(directory, file))
        return result

    def construct_config_object(
        self,
        namespace: str,
        config_files: list,
        schema_file: str = "",
        first_file_mandatory: bool = False,
    ) -> Config:
        cache_keys = config_files.copy()
        cache_keys.append(namespace)
        cache_keys.append(self._working_directory_conf_path)
        cache = Cache(self._cache_directory_path, cache_keys, App.CACHE_LIFETIME)

        if not self.is_debug_enabled():
            try:
                return Config(cache.get())
            except CacheNotFoundException:
                pass

        try:
            config_reader = YamlConfigReader(
                config_files[0], required=first_file_mandatory, schema_file=schema_file
            )
            config_object = config_reader.get_config()
            for key in config_files[1:]:
                config_reader = YamlConfigReader(key, schema_file=schema_file)
                config_object.overwrite(config_reader.get_config())
        except ConfigValidationError as e:
            self.logger.error(e)
            self.output.print(
                "Configuration error: {0} at {1} in file {2}",
                [e.message, "/".join(e.error_path), e.file_path],
            )
            raise AppException(
                self.output.format(
                    "Unable to configure application. Fix errors in config file. {}",
                    [e.file_path],
                )
            )

        if not self.is_debug_enabled() and cache is not None:
            cache.save(config_object.get_all())

        return config_object

    @classmethod
    def get_args(cls):
        return sys.argv

    def get_config_object(self) -> CommandsConfig:
        return self._config_object

    def init_object_manager(self):
        self._object_manager = pinject.new_object_graph()

    def get_object_manager(self) -> pinject.object_graph.ObjectGraph:
        return self._object_manager

    # Init section>

    # < App Business logic section
    def run(self):
        if self.is_interactive():
            """Interactive shell for current command"""
            from lcli.app_mode.interactive import LcliPrompt

            LcliPrompt(self, " ".join(self._current_command)).run()
        else:
            """Fire application expose all commands"""
            from lcli.app_mode.fire import Fire

            Fire(self).run()

    # < App Business logic section

    # <Commands related methods
    def get_commands_wrappers(self) -> CommandWrapperCollection:
        return self._commands_wrappers

    def get_commands(self) -> CommandCollection:
        return self._commands

    def get_command_builder_factory(self):
        from lcli.command.builders import CommandBuilderFactory

        return CommandBuilderFactory(self)

    # Commands related methods>

    def get_app_code(self):
        return self._config_object.get("app_code")

    def get_app_description(self):
        return self._config_object.get("app_description", "")

    # <Flags
    def is_interactive(self):
        return self.FLAG_INTERACTIVE in self._flags

    def is_verbose(self):
        return self.FLAG_VERBOSE in self._flags

    def is_debug_enabled(self):
        return self.FLAG_DEBUG in self._flags

    # Flags>

    # <Directories/Paths
    def get_working_directory(self):
        return self._working_directory

    def get_executable_path(self):
        return self._executable_path

    def get_executable_name(self):
        return self._executable_name

    def get_self_executable_script(self):
        return os.path.join(self.get_executable_path(), self.get_executable_name())

    def get_log_file(self, log_file: str):
        log_path = os.path.join(self._user_home_directory_path, "log")
        try:
            os.makedirs(log_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return os.path.join(log_path, log_file)

    # Directories/Paths>
    @property
    def cache_directory_path(self):
        return self._cache_directory_path
