import os
import sys
from typing import Optional

from flex_framework.console.input import Input

from ..api.proxy import ProxyContainer, ProxyInterface
from ..logger import Logger, ProfilerLoggerProxy
from ..object_manager import Factory as ObjectManagerFactory
from ..object_manager import ObjectManager
from .constants import APP_CLI_CWD, APP_CLI_ENTRY_POINT


class ApplicationBootstrap:
    _profiler: Logger | ProxyInterface
    _current_working_dir: str
    _arguments: dict
    _object_manager: ObjectManager

    def __init__(
        self,
        object_manager_factory: ObjectManagerFactory,
        current_working_dir: str,
        arguments: dict,
    ):
        self.process_arguments(arguments)
        self._object_manager = object_manager_factory.create(arguments)
        console_input: Input = self._object_manager.provide(Input)
        cwd = console_input.namespace.cwd
        if cwd != "":
            current_working_dir = cwd
        cex = console_input.namespace.cex
        if cex != "":
            arguments[APP_CLI_ENTRY_POINT] = cex
        self._current_working_dir = current_working_dir
        arguments[APP_CLI_CWD] = ApplicationBootstrap.process_working_directory(
            current_working_dir
        )

        self._arguments = arguments
        self._profiler = ProxyInterface[ProxyContainer[Logger], Logger](
            self._object_manager, ProfilerLoggerProxy
        )

    @staticmethod
    def create(
        current_working_dir: str,
        params=None,
        object_manager_factory: Optional[ObjectManagerFactory] = None,
    ):
        if params is None:
            params = {}

        if object_manager_factory is None:
            object_manager_factory = ObjectManagerFactory()

        return ApplicationBootstrap(object_manager_factory, current_working_dir, params)

    def create_application(self, instance):
        return self._object_manager.provide(instance)

    def run(self, application):
        self._profiler.info("Start")
        try:
            try:
                try:
                    self.init_error_handler()
                    result = application.launch()
                    result.send_response(lambda: self._profiler.info("Stop"))
                except Exception as exception:
                    application.catch_exception(self, exception)
            except Exception as unhandled_exception:
                application.terminate(unhandled_exception)
        except Exception as unhandled_exception:
            self.terminate(unhandled_exception)

    def init_error_handler(self):
        pass

    def terminate(self, exception: Exception):
        print("Unhandled exception: " + str(exception))
        exit(1)

    def process_arguments(self, arguments: dict):
        arguments["dirs"]["user_home"] = os.path.expanduser("~")
        arguments["dirs"]["user_config"] = os.path.expanduser(
            os.path.join("~", ".config", "flex-cli")
        )
        arguments["dirs"]["user_cache"] = os.path.expanduser(
            os.path.join("~", ".cache", "flex-cli")
        )
        arguments["dirs"]["system_config"] = os.path.join(
            os.path.realpath(arguments["dirs"]["system_config"])
        )
        arguments["dirs"]["cwd_config"] = os.path.join(
            os.getcwd(), ".flex-cli", "config"
        )
        arguments["dirs"]["cwd_cache"] = os.path.join(os.getcwd(), ".flex-cli", "cache")

    @staticmethod
    def process_working_directory(cwd: str = ""):
        if cwd == "":
            cwd = os.getcwd()
        sys.path.append(cwd)
        return cwd
