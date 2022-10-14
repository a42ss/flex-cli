import logging
import os.path

from flex_cli.handler.shell_proxy import ShellProxy
from flex_cli.handler.standalone_executable import StandaloneExecutable
from flex_cli.handler.bash import BashEmulator
from flex_framework.api.handler import HandlerInterface, get_handler

params = {
    HandlerInterface.Const.DEFAULT_HANDLER: get_handler(BashEmulator),
    "handlers": {
        "flex": {
            "bash": {
                "emulator": get_handler(BashEmulator),
                "standalone": get_handler(StandaloneExecutable),
                "proxy": get_handler(ShellProxy)
            }
        }
    },
    "logger": {
        "application": {
            "file": "application.log",
            "verbosity": logging.INFO,
        },
        "debug": {
            "file": "debug.log",
            "verbosity": logging.DEBUG
        },
        "profiler": {
            "file": "profiler.log",
            "verbosity": logging.DEBUG
        }
    }
}
