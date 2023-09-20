import argparse
import sys
from argparse import Namespace
from typing import Optional


class Input:
    configuration: dict
    original_argv: list[str]
    namespace: Namespace
    handler: str
    processed_arguments: list[str]

    def __new__(cls, configuration: Optional[dict] = None):
        if not hasattr(cls, "instance"):
            cls.instance = super(Input, cls).__new__(cls)
            cls.init(cls.instance, configuration)
        return cls.instance

    def __init__(self, configuration: Optional[dict] = None):
        pass

    @staticmethod
    def init(instance, configuration: Optional[dict] = None):
        if configuration is None:
            configuration = {}
        instance.configuration = configuration
        instance.original_argv = sys.argv
        parser = argparse.ArgumentParser(
            description="Flex cli",
            add_help=bool(configuration.get("add_help")),
            prefix_chars="-",
        )
        argument_type = "-"

        handler_arguments = instance.configuration.get("handler_arguments")
        if isinstance(handler_arguments, dict) and handler_arguments.get("positional"):
            argument_type = ""
        parser.add_argument(
            argument_type + "handler",
            nargs="?",
            const="default",
            default="default",
            help="Handler used to process the request",
        )
        parser.add_argument(
            argument_type + "cwd",
            nargs="?",
            const="",
            default="",
            help="Current working directory for the application.",
        )
        parser.add_argument(
            argument_type + "cex",
            nargs="?",
            const="",
            default="",
            help="Entry point for the console script. Overwrite the name of the executable script.",
        )
        parser.add_argument(
            "--flush-cache",
            action="store_true",
            help="Remove all layers of cache for the application.",
        )
        parser.add_argument(
            "--version", action="store_true", help="Show FlexCli version"
        )
        (namespace, processed_arguments) = parser.parse_known_args()
        instance.namespace = namespace
        instance.handler = namespace.handler
        instance.processed_arguments = processed_arguments
        sys.argv = [instance.original_argv[0]] + processed_arguments
