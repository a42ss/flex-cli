import os

import ansible.cli
from ansible.cli.playbook import PlaybookCLI
from ansible.playbook import Playbook

from lcli.app import App
from lcli.command.builders import BaseBuilder
from lcli.command.wrappers import BaseCommandWrapperInterface, BashCommandWrapper
from lcli.config import Command, CommandCollection


class AnsibleWrapper(BashCommandWrapper, BaseCommandWrapperInterface):
    """
    Wrapp ansible command with autocomplete and suggestions functionality
    """

    _command_name: str
    _command: Command

    def __init__(self, app: App, command: Command) -> None:
        command = self.__init_playbook_methods(app, command)
        super().__init__(app, command)

    def __init_playbook_methods(self, app: App, command: Command):
        arguments = ["ansible-playbook"]

        playbook_path = os.path.abspath(command.args.get("playbook"))
        arguments.append(playbook_path)
        arguments.append("-i")
        arguments.append(command.args.get("inventory"))

        cli = PlaybookCLI(arguments)
        cli.parse()
        loader, inventory, variable_manager = cli._play_prereqs()
        pb = Playbook.load(
            playbook_path, variable_manager=variable_manager, loader=loader
        )
        plays = pb.get_plays()
        play: ansible.playbook.play.Play
        command_dict = {}
        for play in plays:
            command_dict[play.vars["lcli"]["id"]] = {
                "description": play.vars["lcli"]["description"],
                "name": play.vars["lcli"]["id"],
                "type": "cli",
                "args": {
                    "command": " ".join(
                        [
                            "ansible-playbook",
                            playbook_path,
                            "-i",
                            command.args.get("inventory"),
                            "--tags=security,performance,db_servers",
                        ]
                    )
                },
            }

        command = command.get()
        command["commands"] = CommandCollection(command_dict)
        return Command(command["name"], command)

    class _Builder(BaseBuilder):
        """
        This will be a custom builder for current wrapper, custom ones may be implemented
        """

        command_type: str = "ansible_wrapper"

        def build(self, command: Command) -> "AnsibleWrapper":
            return AnsibleWrapper(self._app, command)
