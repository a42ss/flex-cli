import os
import sys

import pinject

from flex_cli.handler.debug import DebugHandler
from flex_framework.config import Deployment
from flex_framework.config.discover import ConfigDirectories
from flex_framework.console import Input
from flex_framework.console.otput import CliResponse
from flex_framework.environment import EnvironmentManager
from flex_framework.filesystem import FileDiscovery, FileDiscoveryChecks


class ConfigDebugHandler(DebugHandler):
    file_discovery: FileDiscovery
    config_directories: ConfigDirectories

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    @pinject.annotate_arg("console_input", "flex_framework.console.input.Input")
    def __init__(
            self,
            deployment_config: Deployment,
            console_input: Input,
            environment: EnvironmentManager,
            config_directories: ConfigDirectories,
            file_discovery: FileDiscovery,
    ):
        super().__init__(deployment_config, console_input, environment)
        self.file_discovery = file_discovery
        self.config_directories = config_directories

    def handle(self) -> CliResponse:
        available_directories = self.config_directories.get_available_directories()

        file_checks = FileDiscoveryChecks(
            FileDiscoveryChecks.PERMISSION_CHECK_R,
            FileDiscoveryChecks.PERMISSION_CHECK_NONE,
            FileDiscoveryChecks.PERMISSION_CHECK_W,
            ["yaml"]
        )
        available_config_files = self.file_discovery.get_available_files(
            available_directories,
            file_checks=file_checks
        )
        return CliResponse.Factory.create(0, str(available_config_files))


def process_working_directory():
    cwd = os.getcwd()
    sys.path.append(cwd)
    return cwd
