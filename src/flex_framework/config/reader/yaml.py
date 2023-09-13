import json
import os

import yaml
from jsonschema import ValidationError, validate

from ..exception import ConfigException, ConfigValidationError
from . import ConfigReader


class YamlConfigReader(ConfigReader):
    _schema_file: str

    def __init__(self, config_path: str, required: bool = False, schema_file: str = ""):
        self._schema_file = schema_file
        super().__init__(config_path, required)

    def read_config(self) -> dict:
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
