from ..exceptions import FlexException


class ConfigException(FlexException):
    error_code: int = 1000


class InvalidConfigurationMergeParams(ConfigException):
    error_code: int = 1001


class ConfigValidationError(ConfigException):
    error_code: int = 1002
    file_path: str
    message: str
    error_path: list

    def __init__(self, file_path: str, message: str, error_path=None):
        if error_path is None:
            error_path = []
        self.error_path = error_path
        self.message = message
        self.file_path = file_path


class FilesystemException(FlexException):
    error_code: int = 2000
