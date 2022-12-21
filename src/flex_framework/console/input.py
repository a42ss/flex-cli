import argparse
import sys
from argparse import Namespace


class Input:
    configuration: dict
    original_argv: list[str]
    namespace: Namespace
    handler: str
    processed_arguments: list[str]

    def __init__(self, configuration: dict = None):
        if configuration is None:
            configuration = {}
        self.configuration = configuration
        self.original_argv = sys.argv

        parser = argparse.ArgumentParser(
            description="Flex cli", add_help=True, prefix_chars="-"
        )
        argument_type = "-"

        handler_arguments = self.configuration.get("handler_arguments")
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
            "--flush-cache",
            action="store_true",
            help="Remove all layers of cache for the application.",
        )
        parser.add_argument(
            "--version", action="store_true", help="Show FlexCli version"
        )
        (namespace, processed_arguments) = parser.parse_known_args()
        self.namespace = namespace
        self.handler = namespace.handler
        self.processed_arguments = processed_arguments
        sys.argv = [self.original_argv[0]] + processed_arguments
