from __future__ import annotations

import copy
from typing import Optional

from .exception import ConfigException
from .merge import dict_merge


class Config(dict):
    """
    Base config command for projects, extend to achieve the needed flexible, extensible data object
    """

    _config: dict

    def __init__(self, config_data: Optional[dict] = None):
        super().__init__()
        if config_data is None:
            config_data = {}
        self._config = config_data

    def __getitem__(self, key: str) -> Config:
        return self._config[key]

    def __contains__(self, key: object) -> bool:
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
