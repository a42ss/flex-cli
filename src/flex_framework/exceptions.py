from .api.exception import FlexExceptionInterface


class FlexException(FlexExceptionInterface):
    pass


class GeneralException(FlexExceptionInterface):
    error_code: int = 1


class UnexpectedException(FlexExceptionInterface):
    error_code: int = 9999


class BuilderException(FlexException):
    pass
