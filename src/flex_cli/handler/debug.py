import pinject

from flex_framework.config import Deployment
from flex_framework.console.handler import Handler, HandlerException
from flex_framework.console.input import Input
from flex_framework.console.otput import CliResponse
from flex_framework.environment import EnvironmentManager


class DebugHandler(Handler):
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
        raise HandlerException('The method "handle" is not implemented.')
