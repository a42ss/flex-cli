import os
import subprocess
import sys


class StandaloneExecutable:
    class Config:
        ENV_FLEX_CLI_EXE: str = "FLEX_CLI_EXE"
        ENV_FLEX_CLI_DEBUG: str = "FLEX_CLI_DEBUG"
        ENV_DEFAULT_CLI_EXECUTABLE: str = "flex-cli"

    def __init__(self, file_path: str):
        flex_cli_executable = os.environ.get(self.Config.ENV_FLEX_CLI_EXE)
        flex_cli_debug = os.environ.get(self.Config.ENV_FLEX_CLI_DEBUG)

        if flex_cli_executable is None:
            flex_cli_executable = self.Config.ENV_DEFAULT_CLI_EXECUTABLE

        console_absolute_path = os.path.abspath(os.path.realpath(file_path))
        command_namespace = os.path.basename(console_absolute_path)
        file_path = os.path.dirname(console_absolute_path)

        arguments = [flex_cli_executable, command_namespace]
        arguments.extend(sys.argv[1:])
        arguments.append("--cwd")
        arguments.append(file_path)

        if flex_cli_debug is not None:
            print(arguments)

        subprocess_execution = subprocess.run(arguments)

        if flex_cli_debug is not None:
            print("The exit code was: %d" % subprocess_execution.returncode)
