import pinject

from flex_framework.console.handler import Handler
from flex_framework.console.input import Input
from flex_framework.console.otput import CliResponse
from flex_framework.environment import EnvironmentManager
from flex_framework.shell.bash import BashEmulatorFlexAware


class BashEmulator(Handler):
    _environment: EnvironmentManager
    _input: Input

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("console_input", "flex_framework.console.input.Input")
    def __init__(self, environment: EnvironmentManager, console_input: Input):
        self._environment = environment
        self._input = console_input

    def handle(self) -> CliResponse:
        bash_emulator = BashEmulatorFlexAware(self._environment)
        bash_emulator.emulate_bash()
        return CliResponse.Factory.create(0)
