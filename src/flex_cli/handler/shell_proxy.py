import pinject

from flex_framework.config import Deployment
from flex_framework.console.handler import Handler
from flex_framework.console.input import Input
from flex_framework.console.otput import CliResponse
from flex_framework.environment import EnvironmentManager
from flex_framework.shell.proxy import SimpleShellProxy


class ShellProxy(Handler):
    _environment: EnvironmentManager
    _input: Input

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    @pinject.annotate_arg("console_input", "flex_framework.console.input.Input")
    def __init__(
        self,
        deployment_config: Deployment,
        console_input: Input,
        environment: EnvironmentManager,
    ):
        self._deployment_config = deployment_config
        self._input = console_input
        self._environment = environment

    def handle(self) -> CliResponse:
        shell_proxy = SimpleShellProxy(self._environment)
        from flex_framework.application.constants import (
            APP_CLI_CWD,
            APP_CLI_ENTRY_POINT,
        )

        entry_point = self._deployment_config.get(APP_CLI_ENTRY_POINT)
        cwd = self._deployment_config.get(APP_CLI_CWD)
        exit_code = shell_proxy.execute(entry_point, cwd)
        return CliResponse.Factory.create(exit_code)
