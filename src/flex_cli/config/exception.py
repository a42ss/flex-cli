from flex_framework.exceptions import FlexException


class ConfigException(FlexException):
    error_code: int = 1000


class InvalidConfigurationMergeParams(ConfigException):
    error_code: int = 1001
