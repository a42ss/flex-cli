import os

from flex_framework.api.application import ApplicationInterface, T
from flex_framework.application import ApplicationBootstrap as BaseApplicationBootstrap
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
        params["entry_point"] = entry_point

        current_working_dir = os.path.basename(entry_point)

        return BaseApplicationBootstrap.create(
            current_working_dir, params, object_manager_factory
        )


class SimpleApplicationRuner(ApplicationInterface[CliResponse]):
    def launch(self) -> T:
        raise Exception("Launch method is disabled for this application type.")

    default_handler: object
    entry_point: str

    def __init__(self, entry_point: str, default_handler: object):
        self.default_handler = default_handler
        self.entry_point = entry_point

    def run(self):
        from ..etc import extend_env_variables
        from ..etc.env import params
        from .flex_cli import FlexCli

        bootstrap = ApplicationBootstrap.create_with_file_name(
            self.entry_point, extend_env_variables(params, self.default_handler)
        )
        application = bootstrap.create_application(FlexCli)
        bootstrap.run(application)
