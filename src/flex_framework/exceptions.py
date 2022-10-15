from pinject.errors import Error as PinjectGeneralError

from .api.exception import FlexExceptionInterface


class FlexException(FlexExceptionInterface):
    pass


class GeneralException(FlexExceptionInterface):
    error_code: int = 1
    exit_code: int = 254


class FactoryException(FlexExceptionInterface):
    error_code: int = 2000


class ObjectManagerException(FlexExceptionInterface, PinjectGeneralError):
    error_code: int = 3000


class UnexpectedException(FlexExceptionInterface):
    error_code: int = 9999
    exit_code: int = 255


class BuilderException(FlexException):
    pass
