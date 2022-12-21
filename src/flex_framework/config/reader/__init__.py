from .. import Config
from ..exception import ConfigException


class ConfigReader(object):
    """
    Read the configuration from the files, this is the base functionality
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
