import os
import subprocess
import sys

import pinject

from ..environment.manager import Environment as EnvironmentManager


class SimpleShellProxy:
    _environment: EnvironmentManager
    env_path_to_remove: list
    env: dict[str, str]

    class Config:
        ENV_LOCAL_PATH: str = "FLEX_SHELL_PROXY_LOCAL_PATH"

    @pinject.copy_args_to_internal_fields
    def __init__(self, environment: EnvironmentManager, env_path_to_remove=None):
        if env_path_to_remove is None:
            env_path_to_remove = SimpleShellProxy.get_local_path_items()
        self.env_path_to_remove = env_path_to_remove

        self.env = os.environ.copy()
        all_paths = self.env["PATH"].split(":")
        for path_to_remove in self.env_path_to_remove:
            for path in all_paths:
                if os.path.abspath(path) == os.path.abspath(path_to_remove):
                    all_paths.remove(path)
        self.env["PATH"] = ":".join(all_paths)

    @staticmethod
    def get_global_command_arguments() -> list:
        return []

    @staticmethod
    def get_arguments():
        command_arguments = []
        for arg in sys.argv[1:]:
            command_arguments.append('"' + arg + '"')
        return command_arguments

    def execute(
        self, command: str, cwd: str | None = None, append_arguments: bool = True
    ) -> int:
        if append_arguments:
            global_command_arguments = self.get_global_command_arguments()
            if len(global_command_arguments):
                command += " " + " ".join(global_command_arguments)
            arguments = self.get_arguments()
            if len(arguments):
                command += " " + " ".join(arguments)
        try:
            return subprocess.call(
                command,
                shell=True,
                env=self.env,
                executable=self.env.get("SHELL"),
                cwd=cwd,
            )
        except KeyboardInterrupt:
            return 0
        except Exception:
            return 1

    @staticmethod
    def get_local_path_identifier():
        return SimpleShellProxy.Config.ENV_LOCAL_PATH

    @staticmethod
    def get_local_path_items() -> list:
        if SimpleShellProxy.Config.ENV_LOCAL_PATH in os.environ:
            return os.environ[SimpleShellProxy.Config.ENV_LOCAL_PATH].split(":")
        return []
