import logging

import flex_framework.config
import flex_framework.console.handler
import flex_framework.environment
import flex_framework.filesystem
import flex_framework.logger
from flex_cli.handler.bash import BashEmulator
from flex_cli.handler.shell_proxy import ShellProxy
from flex_cli.handler.standalone_executable import StandaloneExecutable
from flex_framework.api.handler import HandlerInterface, get_handler


params = {
    "dirs": {"system_config": "/etc/flex-cli"},
    "configuration": {
        "locations": ["SYS" "HOME" "CWD"],
        "path_namespaces": ["flex-cli", ".flex-cli"],
    },
    "input": {"flex_add_help": True},
    HandlerInterface.Const.DEFAULT_HANDLER: get_handler(BashEmulator),
    "handlers": {
        "flex": {
            "bash": {
                "emulator": get_handler(BashEmulator),
                "standalone": get_handler(StandaloneExecutable),
                "proxy": get_handler(ShellProxy),
            }
        }
    },
    "logger": {
        "application": {
            "file": "application.log",
            "verbosity": logging.INFO,
        },
        "debug": {"file": "debug.log", "verbosity": logging.DEBUG},
        "profiler": {"file": "profiler.log", "verbosity": logging.DEBUG},
    },
    "di": {
        "modules": [
            flex_framework.logger,
            flex_framework.environment,
            flex_framework.console.input,
            flex_framework.console.handler,
            flex_framework.config.deployment,
            flex_framework.filesystem,
        ],
        "classes": [flex_framework.logger.Logger],
        "binding_specs": [
            flex_framework.config.ObjectManagerSpec,
            flex_framework.console.ObjectManagerSpec,
            flex_framework.logger.ObjectManagerSpec,
        ],
    },
}
