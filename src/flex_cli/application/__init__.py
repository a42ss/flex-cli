from typing import Optional

from flex_framework.api.application import ApplicationInterface, T
from flex_framework.application import ApplicationBootstrap as BaseApplicationBootstrap
from flex_framework.application.constants import APP_CLI_ENTRY_POINT
from flex_framework.config.merge import dict_merge
from flex_framework.console.otput import CliResponse
from flex_framework.object_manager import Factory as ObjectManagerFactory


class ApplicationBootstrap(BaseApplicationBootstrap):
    @staticmethod
    def create_with_file_name(
        entry_point: str,
        params=None,
        object_manager_factory: ObjectManagerFactory = None,
    ):
        if params is None:
            params = {}
        params[APP_CLI_ENTRY_POINT] = entry_point
        current_working_dir = BaseApplicationBootstrap.process_working_directory()

        return BaseApplicationBootstrap.create(
            current_working_dir, params, object_manager_factory
        )


class SimpleApplicationRuner(ApplicationInterface[CliResponse]):
    params: dict | None

    def launch(self) -> T:
        raise Exception("Launch method is disabled for this application type.")

    default_handler: object
    entry_point: str

    def __init__(
        self, entry_point: str, default_handler: object, params: Optional[dict] = None
    ):
        if params is None:
            params = {}
        self.params = params
        self.entry_point = entry_point
        self.default_handler = default_handler

    def run(self):
        from ..etc import extend_env_variables
        from ..etc.env import params as default_params
        from .flex_cli import FlexCli

        params = dict_merge(default_params, self.params)
        self.params = extend_env_variables(params, self.default_handler)

        bootstrap = ApplicationBootstrap.create_with_file_name(
            self.entry_point, self.params
        )
        application = bootstrap.create_application(FlexCli)
        bootstrap.run(application)
