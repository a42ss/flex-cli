from .api.exception import FlexExceptionInterface


class FlexException(FlexExceptionInterface):
    pass


class UnexpectedException(FlexExceptionInterface):
    error_code: int = 9999


class BuilderException(FlexException):
    pass