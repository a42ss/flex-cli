import copy
import os
from typing import Dict

from lcli.exceptions import LcliException


class ConfigException(LcliException):
    pass


class ConfigNamespaces(object):
    COMMANDS: str = "commands"


class Config(object):
    """
    Base config command for projects, extend to achieve the needed flexible, extensible data object
    """

    _config: dict

    def __init__(self, config_data: dict = {}):
        self._config = config_data

    def __getitem__(self, key: str) -> "Config":
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        return self._config.__contains__(key)

    def __len__(self):
        return len(self._config)

    def __iter__(self):
        return self._config.__iter__()

    def get_property(self, property_name):
        """
        Return the value of a given key
        :param property_name:
        :return:
        """
        if property_name not in self._config.keys():
            return None
        return self._config[property_name]

    @classmethod
    def _parse_path(cls, path=None):
        """
        Convert the path to list of config codes
        :param path:
        :return:
        """
        if path is None:
            path = []
        if type(path) == str:
            path = path.split("/")
        return path

    def get_all(self) -> dict:
        """

        :return: dict
        """
        return self._config

    def get(self, path=None, default=None):
        """
        Return the config found on a given path
        :param path: can be a string separated by / or list of config codes on the needed path
        :param default:
        :return: mixed
        """
        path_list = self._parse_path(path)
        config = self._config
        current_path = ""
        for key in path_list:
            current_path += key
            if config is not None and key in config:
                config = config[key]
            else:
                if default is None:
                    raise ConfigException(
                        'Requested config path not found "' + current_path + '". '
                        'The full path was: "' + path + '".'
                    )
                else:
                    return default
            current_path += "/"

        if config is None:
            return default
        return config

    def overwrite(self, other_config: "Config") -> "Config":
        config_to_merge = other_config.get()
        for k in config_to_merge:
            config_value = config_to_merge[k]
            if k in self._config and isinstance(self._config[k], dict):
                self._config[k] = dict_merge(self._config[k], config_value)
            else:
                self._config[k] = copy.deepcopy(config_value)
        return self


class CommandsConfig(Config):
    """
    Used as commands config holder on the application for commands namespace scope
    A config namespace will be a file name found and loaded form configs directories defined: in global, user, or local place
    """

    class Constants:
        COMMANDS: str = "commands"
        COMMANDS_WRAPPERS: str = "commands_wrappers"
        AVAILABLE_GROUPS: str = "available_groups"
        AVAILABLE_COMMANDS: str = "available_commands"

    def get_commands(self):
        return self.get(self.Constants.COMMANDS)

    def get_commands_wrappers(self):
        return self.get(self.Constants.COMMANDS_WRAPPERS, default={})

    def get_available_groups(self):
        return self.get(self.Constants.AVAILABLE_GROUPS, default={})

    def get_available_commands(self):
        return self.get(self.Constants.AVAILABLE_COMMANDS, default={})

    def is_command_group_available(self, group_name: str) -> bool:
        available_groups = self.get_available_groups()
        if group_name != "" and (
            len(available_groups) == 0
            or available_groups == "all"
            or "all" in available_groups
            or group_name in available_groups
        ):
            return True
        return False

    def is_command_available(self, command_name: str) -> bool:
        available_commands = self.get_available_commands()
        if (
            len(available_commands) == 0
            or available_commands == "all"
            or "all" in available_commands
            or command_name in available_commands
        ):
            return True
        return False


class ConfigReader(object):
    """
    Read the configuration from the files, this is the base funcionality
    """

    _config_file: str
    _config_dict: dict

    def __init__(self, config_path: str, required: bool = False):
        self.required = required
        self._config_file = config_path
        self._config_dict = self.read_config()

    def read_config(self) -> dict:
        """
        Implement read and convert to dict the config file
        :return:
        """
        raise ConfigException(
            "Read config method not implemented for current files type."
        )

    def get_config(self) -> Config:
        """

        :return:
        """
        return Config(self._config_dict)


class ConfigValidationError(BaseException):
    file_path: str
    message: str
    error_path: list

    def __init__(self, file_path: str, message: str, error_path=None):
        if error_path is None:
            error_path = []
        self.error_path = error_path
        self.message = message
        self.file_path = file_path


class YamlConfigReader(ConfigReader):
    _schema_file: str

    def __init__(self, config_path: str, required: bool = False, schema_file: str = ""):
        self._schema_file = schema_file
        super().__init__(config_path, required)

    def read_config(self) -> dict:
        import json

        import yaml
        from jsonschema import ValidationError, validate

        schema = {}
        if os.path.exists(self._schema_file):
            with open(self._schema_file) as f:
                schema = json.load(f)

        config = {}
        if os.path.exists(self._config_file):
            with open(self._config_file, "r") as yml_file_stream:
                config = yaml.safe_load(yml_file_stream)
            try:
                validate(config, schema)
            except ValidationError as e:
                raise ConfigValidationError(self._config_file, e.message, list(e.path))
        else:
            if self.required:
                raise ConfigException(
                    "Invalid configuration file: " + self._config_file
                )
        return config


class Command(Config):
    class Constants:
        COMMANDS: str = "commands"
        NAME: str = "name"
        DESCRIPTION: str = "description"
        TYPE: str = "type"

        class TYPES:
            CLI = "cli"
            LCLI: str = "lcli"
            WRAPPER: str = "wrapper"
            FUNCTION: str = "function"

        ARGS: str = "args"

        EXECUTABLE_COMMAND_TYPES: list = [TYPES.LCLI, TYPES.FUNCTION, TYPES.WRAPPER]

    def __init__(self, command_name: str, config_data: dict):
        config_data[self.Constants.NAME] = command_name
        args = {}
        if self.Constants.ARGS in config_data:
            args = config_data[self.Constants.ARGS]
        config_data[self.Constants.ARGS] = CommandArgs(args)
        if self.Constants.TYPE not in config_data:
            raise ConfigException(
                "Invalid config data. Command type not provided for " + command_name
            )

        if self.Constants.COMMANDS not in config_data:
            config_data[self.Constants.COMMANDS] = CommandCollection({})
        super().__init__(config_data)

    def has_commands(self):
        return len(self) > 0

    def is_executable(self):
        return self.type in self.Constants.EXECUTABLE_COMMAND_TYPES

    @property
    def type(self):
        return self.get_property(self.Constants.TYPE)

    @property
    def commands(self):
        return self.get_property(self.Constants.COMMANDS)

    @property
    def name(self):
        return self.get_property(self.Constants.NAME)

    @property
    def description(self):
        return self.get_property(self.Constants.DESCRIPTION)

    @property
    def args(self) -> "CommandArgs":
        return self.get_property(self.Constants.ARGS)

    def is_group(self):
        return self.type == "group"


class CommandArgs(Config):
    class Constants:
        PARAMS: str = "params"
        EXEC_TYPE: str = "exec_type"
        COMMAND: str = "command"
        CWD: str = "cwd"
        COMMAND_CONFIG: str = "config"

    def __init__(self, config_data: dict):
        if self.Constants.PARAMS in config_data:
            config_data[self.Constants.PARAMS] = CommandArgsParams(
                config_data[self.Constants.PARAMS]
            )
        if self.Constants.COMMAND_CONFIG in config_data:
            config_data[self.Constants.COMMAND_CONFIG] = Config(
                config_data[self.Constants.COMMAND_CONFIG]
            )
        super().__init__(config_data)

    @property
    def exec_type(self) -> str:
        return self.get_property(self.Constants.EXEC_TYPE)

    @property
    def command(self) -> str:
        return self.get_property(self.Constants.COMMAND)

    @property
    def config(self) -> Config:
        return self.get(self.Constants.COMMAND_CONFIG, Config())

    @property
    def params(self) -> "CommandArgsParams":
        return self.get_property(self.Constants.PARAMS)


class CommandArgsParams(Config):
    class Constants:
        pass

    def __init__(self, params: dict):
        _params = {}
        for key in params:
            _params[key] = CommandParam(params[key])
        super().__init__(_params)

    def get_param(self, key: str) -> "CommandParam":
        """

        :param key:
        :return: CommandConfig
        """
        return self.get(key)


class CommandParam(Config):
    class Constants:
        TYPE: str = "type"
        NAME: str = "name"
        OUTPUT_FORMAT: str = "output_format"
        MESSAGE: str = "message"
        CHOICES: str = "choices"
        CHOICES_CMD: str = "choices_cmd"

    def __init__(self, config_data: dict):
        if self.Constants.CHOICES in config_data:
            config_data[self.Constants.CHOICES] = CommandParamChoices(
                config_data[self.Constants.CHOICES]
            )
        if self.Constants.CHOICES_CMD in config_data:
            config_data[self.Constants.CHOICES_CMD] = CommandParamChoicesCmd(
                config_data[self.Constants.CHOICES_CMD]
            )
        super().__init__(config_data)

    @property
    def type(self) -> str:
        return self.get_property(self.Constants.TYPE)

    @property
    def name(self) -> str:
        return self.get_property(self.Constants.NAME)

    @property
    def output_format(self) -> str:
        return self.get_property(self.Constants.OUTPUT_FORMAT)

    @property
    def message(self) -> str:
        return self.get_property(self.Constants.MESSAGE)

    @property
    def choices(self) -> "CommandParamChoices":
        return self.get_property(self.Constants.CHOICES)

    @property
    def choices_cmd(self) -> "CommandParamChoicesCmd":
        return self.get_property(self.Constants.CHOICES_CMD)


class CommandParamChoices(Config):
    class Constants:
        pass

    def __init__(self, choices: dict):
        _params = {}
        for choice in choices:
            _params[choice[CommandParamChoice.Constants.NAME]] = CommandParamChoice(
                choice
            )
        super().__init__(_params)

    def get_choice(self, key: str) -> "CommandParamChoice":
        """

        :param key:
        :return: CommandConfig
        """
        return self.get(key)


class CommandParamChoice(Config):
    class Constants:
        NAME: str = "name"
        VALUE: str = "value"

    @property
    def name(self) -> str:
        return self.get_property(self.Constants.NAME)

    @property
    def value(self) -> str:
        return self.get_property(self.Constants.VALUE)


class CommandParamChoicesCmd(Config):
    class Constants:
        COMMAND: str = "cmd"
        FILTER: str = "filter"

    def is_empty(self):
        return len(self._config) == 0

    @property
    def command(self) -> str:
        return self.get_property(self.Constants.COMMAND)

    @property
    def filter(self) -> dict:
        return self.get_property(self.Constants.FILTER)


class CommandCollection(Config):
    _config: Dict[str, Command]

    def __init__(self, commands: dict):
        _commands = {}
        if "list_type" in commands:
            del commands["list_type"]
        for command_key in commands:
            if Command.Constants.COMMANDS in commands[command_key]:
                sub_commands = CommandCollection(
                    commands[command_key][Command.Constants.COMMANDS]
                )
                commands[command_key][Command.Constants.COMMANDS] = sub_commands

            command = commands[command_key]

            if "cli_code" in command:
                cli_code = command["cli_code"]
                if cli_code is not None and cli_code != "":
                    command_key = cli_code

            _commands[command_key] = Command(command_key, command)
        super().__init__(_commands)

    def get_all(self) -> Dict[str, Command]:
        """

        :return: Dict[str, CommandConfig]
        """
        return self._config

    def get_command(self, command_key: str) -> Command:
        """

        :param command_key:
        :return: CommandConfig
        """
        return self.get(command_key)

    def add_command(self, command: Command) -> "CommandCollection":
        """
        Append a command in current list

        :param command: CommandConfig
        :return: CommandConfig
        """
        self._config[command.name] = command
        return self

    def get_commands_names_in_path(
        self, path: list = None, ignored_commands=None, available_groups: list = []
    ) -> dict:
        """
        Get commands names available in a given path

        :param path:
        :param ignored_commands:
        :param available_groups:
        :return: dict containing commands names
        """
        if ignored_commands is None:
            ignored_commands = ["-i", "-v", "-version", "--version", "h", "cli_info"]
        if path is None:
            path = []
        try:
            commands_list = self._get_command_collection_by_path(self, path)
            return self.get_first_level_commands(
                commands_list, ignored_commands, available_groups=available_groups
            )
        except ConfigException:
            return {}

    def get_first_level_commands(
        self,
        commands_list: "CommandCollection",
        ignored_commands: list,
        available_groups: list = [],
    ) -> dict:
        """
        Returns the directly/first accessible commands for a command list
        Commands of type group are not needed to address a command in commands hierarchy
        For this reason the first level command for a command list are the first level commands that are not group

        :param commands_list:
        :param ignored_commands:
        :param available_groups:
        :return: dict containing the first level commands described above
        """
        result = {}
        if type(commands_list) == CommandCollection:
            for key in commands_list:
                if key in ignored_commands:
                    continue
                command = commands_list.get_command(key)
                if command.is_group():
                    if command.name in available_groups:
                        sub_class_commands = self.get_first_level_commands(
                            command.commands, ignored_commands
                        )
                        for sub_command_key in sub_class_commands:
                            result[sub_command_key] = sub_class_commands[
                                sub_command_key
                            ]
                else:
                    result[command.name] = command.name
        return result

    def get_command_collection_by_path(
        self, path: list = None, return_deepest=False
    ) -> "CommandCollection":
        """
        Return the list of commands accessed by a given path for invocation

        :param path: a list of strings representing the command codes
        :param return_deepest: - return the deepest found path
        :return:
        :raise: lcli.exception.ConfigException
        """
        if path is None:
            path = []
        return self._get_command_collection_by_path(
            self, path, return_deepest=return_deepest
        )

    def _get_command_collection_by_path(
        self,
        commands_list: "CommandCollection",
        path: list = None,
        return_deepest=False,
    ) -> "CommandCollection":
        """
        Return the list of commands accessed by a given path for invocation

        :param commands_list:
        :param path: a list of strings representing the command codes
        :param return_deepest: - return the deepest found path
        :return:
        :raise: lcli.exception.ConfigException
        """
        key_index = 0
        if path is None:
            path = []
        path = list(path)
        for key in path:
            if commands_list and len(commands_list) > 0 and key in commands_list:
                command = commands_list.get_command(key)
                commands_list = command.commands
            else:
                found_command = False
                for command_key in commands_list:
                    command = commands_list.get_command(command_key)
                    if command.is_group():
                        commands_list = self._get_command_collection_by_path(
                            command.commands, path[key_index:]
                        )
                        found_command = True
                        break
                if not found_command:
                    if return_deepest:
                        return commands_list
                    raise ConfigException("Broken command path")
            key_index += 1
        return commands_list

    def get_command_by_path(self, path: list = None, return_first_executable=False):
        """
        Return the command accessed by a given path

        :param path: a list of strings representing the command codes
        :param return_first_executable:
        :return:
        :raise: lcli.exception.ConfigException
        """
        if path is None:
            path = []
        return self._get_command_by_path(
            self, path, return_first_executable=return_first_executable
        )

    def _get_command_by_path(
        self,
        commands_list: "CommandCollection",
        path: list = None,
        return_first_executable=False,
    ):
        """
        Return the command accessed by a given path

        :param commands_list:
        :param path: a list of strings representing the command codes
        :param return_first_executable: - return the deepest found path
        :return:
        :raise: lcli.exception.ConfigException
        """
        if path is None:
            path = []
        path = list(path)
        path_len = len(path)
        if path_len == 0:
            return None
        current_path = path[0]
        command = None
        if commands_list and len(commands_list) > 0 and current_path in commands_list:
            command = commands_list.get_command(current_path)
            if return_first_executable and command.is_executable():
                return command
            if path_len > 1:
                command = self._get_command_by_path(
                    command.commands,
                    path[1:],
                    return_first_executable,
                )
        else:
            for command_key in commands_list:
                command_i = commands_list.get_command(command_key)
                if command_i.is_group():
                    command = self._get_command_by_path(
                        command_i.commands,
                        path,
                        return_first_executable,
                    )
                    if command is not None:
                        return command

        if command is not None:
            return command

        raise ConfigException("Could not identify the command by path")


class CommandWrapper(Config):
    class Constants:
        HANDLER: str = "handler"
        BUILDER: str = "builder"
        ARGS_CONFIG: str = "args_config"

    @property
    def handler(self) -> str:
        return self.get_property(self.Constants.HANDLER)

    @property
    def args_config(self) -> str:
        return self.get_property(self.Constants.ARGS_CONFIG)

    @property
    def builder(self) -> str:
        return self.get_property(self.Constants.BUILDER)


class CommandWrapperCollection(Config):
    class Constants:
        WRAPPERS = "wrappers"

    def __init__(self, wrappers: dict):
        _wrappers = {}
        for key in wrappers:
            _wrappers[key] = CommandWrapper(wrappers[key])
        super().__init__(_wrappers)


def dict_merge(a, b):
    """recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and behave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary."""
    if not isinstance(b, dict):
        return b
    result = copy.deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
            continue

        # todo: implement list merging
        # if isinstance(v, list) and k in result and isinstance(result[k], list):
        #     result[k] = dict_list(result[k], v)
        #     continue

        result[k] = copy.deepcopy(v)
    return result


def dict_list(list1: list, list2: list):
    result = {}
    for value1 in list1:
        result[value1] = value1
    for value2 in list2:
        result[value2] = value2

    return list(result.values())
