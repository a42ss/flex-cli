import pinject

from flex_framework.api.application import (
    ApplicationInterface,
    ApplicationResultInterface,
)
from flex_framework.api.exception import FlexExceptionInterface
from flex_framework.console.handler import HandlerRouter, HandlerRouterFactory
from flex_framework.console.input import Input
from flex_framework.console.otput import CliResponse
from flex_framework.environment import EnvironmentManager
from flex_framework.exceptions import GeneralException, UnexpectedException
from flex_framework.logger import Logger


class FlexCli(ApplicationInterface[CliResponse]):
    _logger: Logger
    _handler_router_factory: HandlerRouterFactory
    _environment: EnvironmentManager
    _input: Input

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("console_input", "flex_framework.console.input.Input")
    @pinject.annotate_arg("logger", "flex_framework.logger.application")
    def __init__(
        self,
        environment: EnvironmentManager,
        console_input: Input,
        handler_router_factory: HandlerRouterFactory,
        logger: Logger,
    ):
        self._environment = environment
        self._input = console_input
        self._handler_router_factory = handler_router_factory
        self._logger = logger

    def launch(self) -> ApplicationResultInterface:
        try:
            handler_router: HandlerRouter = self._handler_router_factory.create(
                HandlerRouter
            )
            handler = handler_router.find(
                handler_router.create_handler_path(self._input.handler)
            )
            result: ApplicationResultInterface = handler.handle()
            return result
        except UnexpectedException as exception:
            self._logger.exception(exception)
            return CliResponse.Factory.create(
                exception.get_exit_code(),
                "Unexpected error, please check the application log for more details",
            )
        except FlexExceptionInterface as exception:
            self._logger.exception(exception)
            return CliResponse.Factory.create(
                exception.get_exit_code(), exception.get_message()
            )
        except Exception as exception:
            self._logger.exception(exception)
            return CliResponse.Factory.create(
                GeneralException.exit_code,
                "Unexpected error, please check the application log for more details",
            )
