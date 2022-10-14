import pinject
import os

from flex_framework.config import Deployment
from flex_framework.console.handler import Handler
from flex_framework.console.otput import CliResponse
from flex_framework.shell.proxy import SimpleShellProxy
from flex_framework.environment import EnvironmentManager
from flex_framework.console.input import Input


class ShellProxy(Handler):
    _environment: EnvironmentManager
    _input: Input

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    @pinject.annotate_arg("input", "flex_framework.console.input.Input")
    def __init__(
            self,
            deployment_config: Deployment,
            input: Input,
            environment: EnvironmentManager
    ):
        self._deployment_config = deployment_config

    def handle(self) -> CliResponse:
        shell_proxy = SimpleShellProxy(self._environment)
        entry_point = os.path.basename(self._deployment_config.get("entry_point"))
        exit_code = shell_proxy.execute(entry_point)
        return CliResponse.Factory.create(exit_code)
