from abc import ABCMeta
from typing import Type

import pinject

from ..api.factory import Factory
from ..api.handler import HandlerInterface
from ..config import Deployment
from ..console.otput import CliResponse
from ..exceptions import FlexException
from ..loader import ClassLoader


class HandlerException(FlexException):
    error_code: int = 3000


class HandlerNotFoundException(FlexException):
    error_code: int = 3001


class HandlerPath(tuple):
    pass


class Handler(HandlerInterface, metaclass=ABCMeta):
    pass


class DebugHandler(Handler):
    def handle(self):
        return CliResponse(CliResponse.Const.EXIT_CODE_SUCCESS, "Debug handler")


class HandlerFactory(Factory[Handler]):
    def create(self, class_name: Type[Handler], data: dict = None) -> Handler:
        return super().create(class_name, data)


class HandlerRouter:
    _deployment_config: Deployment
    _handler_factory: HandlerFactory
    _class_loader: ClassLoader

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    def __init__(
            self,
            deployment_config: Deployment,
            handler_factory: HandlerFactory,
            class_loader: ClassLoader
    ):
        self._deployment_config = deployment_config
        self._handler_factory = handler_factory
        self._class_loader = class_loader

    def find(self, path: HandlerPath) -> Handler:
        try:
            if len(path) > 0 and path[0] is not "default":
                handler_str = self.look_for_handler_in_configuration(path)
                return self.create_handler(handler_str)
        except HandlerNotFoundException:
            pass
        except HandlerException as e:
            print(e.get_message())

        return self.get_default_handler()

    def create_handler_path(self, path: str):
        return HandlerPath(path.split('/'))

    def create_handler(self, handler: str) -> Handler:
        if type(handler) is str:
            handler_class = self._class_loader.locate(handler)
            if handler_class is None:
                raise HandlerException("Invalid handler for: " + handler)

        try:
            return self._handler_factory.create(handler_class)
        except Exception:
            raise HandlerException("Unable to find a handler for: " + handler)

    def get_default_handler(self):
        default_handler = self._deployment_config.get(HandlerInterface.Const.DEFAULT_HANDLER)
        if default_handler is not None:
            return self.create_handler(default_handler)
        raise HandlerException("There is not handler that could execute the current command.")

    def look_for_handler_in_configuration(self, path: HandlerPath):
        handlers = self._deployment_config.get(HandlerInterface.Const.HANDLERS)
        current_handler = handlers
        for item in path:
            if item not in current_handler:
                raise HandlerNotFoundException("Handler not found")
            current_handler = current_handler[item]
        if type(current_handler) is str:
            return current_handler
        raise HandlerException("Unable to find the handler path in the configuration: " + str(path))


class HandlerRouterFactory(Factory[HandlerRouter]):
    pass
