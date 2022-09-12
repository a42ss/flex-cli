import glob
import os

from lcli import __version__
from lcli.app import App
from lcli.tools.base import BaseTool


class Helper(BaseTool):
    """Application helper"""

    def __init__(self, app: App) -> None:
        super().__init__(app)

    def groups(self) -> list:
        """List all command groups"""
        available_groups = self._app.get_config_object().get_available_groups()
        result = []
        if len(available_groups) == 0:
            result.append("All")
        else:
            for group in available_groups:
                if group == "-g":
                    continue
                result.append(group)
        return result

    def commands(self):
        """List all command groups"""
        result = []
        available_commands = self._app.get_config_object().get_available_commands()
        if len(available_commands) == 0:
            result.append("All")
        for command in available_commands:
            result.append(command)
        return result

    def cache_clear(self):
        files = glob.glob(
            os.path.join(self._app.cache_directory_path, "*"), recursive=True
        )
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))


def version():
    """Display application version"""
    print("Version: " + __version__)


def verbose():
    """Enable logging"""
    raise Exception("Verbose mode is not available for the moment")
