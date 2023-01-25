import pinject

from flex_cli.application.cli import StandaloneExecutable as StandaloneExecutableClass
from flex_framework.config import Deployment
from flex_framework.console.handler import Handler
from flex_framework.console.otput import CliResponse


class StandaloneExecutable(Handler):
    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    def __init__(self, deployment_config: Deployment):
        self._deployment_config = deployment_config

    def handle(self) -> CliResponse:
        from flex_framework.application.constants import APP_CLI_ENTRY_POINT

        StandaloneExecutableClass(self._deployment_config.get(APP_CLI_ENTRY_POINT))
        return CliResponse.Factory.create(0)
