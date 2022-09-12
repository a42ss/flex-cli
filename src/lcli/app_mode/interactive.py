import os
from cmd import Cmd

from pyfiglet import Figlet

from lcli.api.conroller import ControllerInterface
from lcli.app_mode.base import AppModeBase, AppModeException
from lcli.command.input import ParametersReader
from lcli.command.subprocess import CommandRunner
from lcli.config import Command, CommandArgs
from lcli.input.exctptions import InterruptedInputException
from lcli.input.prompt import AskQuestions
from lcli.tools.base import ToolsException


def run():
    """Run application in interactive mode for best productivity"""
    raise AppModeException("App mode unavailable for the moment")


class LcliPrompt(Cmd, AppModeBase, ControllerInterface):
    from lcli.app import App

    current_command = ""

    prompt_prefix = ""
    prompt = prompt_prefix + "> "
    intro = ""
    space_separator: str
    app_help_message: str

    doc_header = "Interactive cli commands (type help <topic>):"

    _RESET_WORD = "RESET"
    _CANCEL_WORD = "CANCEL"

    _COMMAND_MAPPING = {
        "/": "change_command",
        "//": "reset_command",
        "<": "remove_one_level_command",
        "///": "force_change_command",
        "z": "clear_screen",
    }

    def __init__(
        self, app: App, command_prefix="", completekey="tab", stdin=None, stdout=None
    ):
        super().__init__(completekey, stdin, stdout)
        AppModeBase.__init__(self, app)
        self.do_clear_screen()
        figlet = Figlet(
            width=1000, font=app.get_config_object().get("figlet_font", "digital")
        )
        command_parts = command_prefix.split(" ")
        if command_parts[0] == self._app.get_executable_name():
            command_parts = command_parts[1:]
        self.current_command = " ".join(command_parts)

        cli_code = app.get_app_code()
        self.prompt_prefix = self._app.__.red(cli_code)
        self.space_separator = self._app.get_config_object().get(
            "app_space_separator", "\n\n\n\n"
        )
        self.app_help_message = self._app.get_config_object().get(
            "app_help_message", ""
        )
        self.intro = (
            self.space_separator
            + figlet.renderText(str(cli_code).upper())
            + self.space_separator
            + self._app.__.red(
                self._app.get_config_object().get(
                    "app_welcome_message", "Welcome! Type ? to list commands"
                )
            )
        )
        self.doc_header = self._app.get_config_object().get(
            "app_doc_header", self.doc_header
        )
        self.refresh_prompt()

    def run(self) -> None:
        """Execute interactive shell for managing scripts"""
        self.cmdloop()

    def do_exit(self, inp):
        print(self._app.__.red("Bye"))
        return True

    def help_exit(self):
        print(self._app.__.red("\nExit the application. Shorthand: x, q or Ctrl-D.\n"))

    def refresh_prompt(self):
        self.prompt = self.prompt_prefix
        if self.current_command != "":
            self.prompt += " " + self._app.__.green(self.current_command)

        ignored_cli_info = self._app.get_config_object().get("cli_info_ignore", [])
        info_parts = []
        if self.current_command not in ignored_cli_info:
            info_parts = self._invoke_command(
                self.current_command, "cli_info", "list", default=[]
            )

        command_state = ""
        for part in info_parts:
            command_state += " (" + self._app.__.yellow(part) + ")"
        self.prompt += command_state
        self.prompt += "\n> "

    def do_clear_screen(self, command=""):
        """Clear the screen and move the cursor to the top"""
        os.system("cls" if os.name == "nt" else "clear")
        self.stdout.write(str(self.intro) + "\n")

    def do_reset_command(self, command=""):
        """Reset current command prefix. This will allow to run any of cli commands."""
        self.current_command = ""
        self.refresh_prompt()

    def do_remove_one_level_command(self, command=""):
        """Remove one level of the current command"""
        self.current_command = " ".join(self.current_command.split(" ")[0:-1])
        self.refresh_prompt()

    def do_force_change_command(self, command=""):
        """Force change interactive command prefix. This will allow running sub-commands from chosen group."""
        self.current_command = ""
        self.do_change_command("")

    def do_change_command(self, command=""):
        """Change interactive command prefix. This will allow running sub-commands from chosen group."""
        if command == "":
            path = []
            if self.current_command != "":
                path = self.current_command.split()

            available_buttons = {self._CANCEL_WORD: {"text": self._CANCEL_WORD}}
            if self.current_command != "":
                available_buttons[self._RESET_WORD] = {"text": self._RESET_WORD}

            names_in_path = self._app.get_commands().get_commands_names_in_path(
                path,
                available_groups=self._app.get_config_object().get_available_groups(),
            )
            names_in_path_list = [k for k in names_in_path]
            names_in_path_list.sort()
            if len(names_in_path_list) == 0:
                names_in_path_list = {self._CANCEL_WORD: "N/A"}

            question = {
                "type": "list",
                "name": "command",
                "message": "Choose a command: ",
                "buttons": available_buttons,
                "choices": names_in_path_list,
            }
            try:
                questions = AskQuestions({"command": question})
                answers = questions.ask()
            except InterruptedInputException:
                return

            if "command" in answers:
                if answers["command"] is None:
                    return

                if answers["command"] == self._RESET_WORD:
                    self.current_command = ""
                elif answers["command"] == self._CANCEL_WORD:
                    pass
                else:
                    separator = ""
                    if self.current_command != "":
                        separator = " "
                    self.current_command += separator + answers["command"]
            else:
                print("Empty selected command. Please try again ...")
                self.do_change_command(command)
        else:
            self.current_command = command

        self.refresh_prompt()

    def complete_change_command(self, text, line, begidx, endidx):
        path = []
        if line != "":
            path = line.split()
        available_commands = []
        for command in self._app.get_commands().get_commands_names_in_path(
            path[1:],
            available_groups=self._app.get_config_object().get_available_groups(),
        ):
            available_commands.append(command)
        print(available_commands)
        return [i for i in available_commands if i.startswith(text)]

    @classmethod
    def help_change_command(cls):
        """Change interactive command prefix. This will allow running sub-commands from chosen group."""
        print("Change interactive command prefix.")
        print("This will allow running sub-commands from chosen group.")

    def emptyline(self):
        if self.current_command != "help":
            command_parts = self.current_command.split(" ")
            if command_parts[0] == self._app.get_executable_name():
                command_parts = command_parts[1:]
            if len(command_parts) > 1:
                command_path = " ".join(command_parts[:-1])
                command_key = command_parts[-1]
            else:
                command_path = self.current_command
                command_key = ""

            returned_value = self._invoke_command(command_path, command_key)
            self._print_command_result(returned_value)
        else:
            self.do_help({})

    def do_help(self, arg):
        """Show help message for interactive mode."""
        super().do_help(arg)
        self.stdout.write("%s\n" % self.app_help_message)

    def default(self, inp):
        if inp == "x" or inp == "q":
            return self.do_exit(inp)
        command = inp
        returned_value = self._invoke_command(self.current_command, command)
        self._print_command_result(returned_value)
        self.refresh_prompt()

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            import readline

            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped

            cmd = ""
            if begidx > 0:
                cmd, args, foo = self.parseline(line)
                if cmd == "" or cmd is None:
                    compfunc = self.complete_command
                else:
                    try:
                        compfunc = getattr(self, "complete_" + cmd)
                    except AttributeError:
                        compfunc = self.complete_command
            else:
                compfunc = self.completenames

            if not hasattr(self, "complete_" + cmd) and self.current_command != "":
                compfunc = self.complete_command

            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def completenames(self, text, *ignored):
        dotext = "do_" + text
        available_commands = [a[3:] for a in self.get_names() if a.startswith(dotext)]
        for cc in self._app.get_commands().get_commands_names_in_path(
            [], available_groups=self._app.get_config_object().get_available_groups()
        ):
            if cc.startswith(text):
                available_commands.append(cc)
        return available_commands

    def complete_command(self, text, line: str, begidx, endidx):
        parts = line.rstrip().split(" ")
        sub_command = " ".join(parts[1:-1])
        if self.current_command != "":
            current_command = self.current_command
        else:
            current_command = parts[0]
        cmd = current_command + " " + sub_command

        available_commands = self._invoke_command(cmd, "h", "list", default=[])
        return [i for i in available_commands if i.startswith(text)]

    def parseline(self, line):
        line = line.strip()
        parts = line.split()
        if not line:
            return None, None, line
        else:
            if parts[0] in self._COMMAND_MAPPING:
                line = self._COMMAND_MAPPING[parts[0]] + " " + " ".join(parts[1:])
        return super().parseline(line)

    do_EOF = do_exit
    help_EOF = help_exit

    def get_full_shell_command(self, cmd: str):
        return self._app.get_self_executable_script() + " " + cmd

    def _invoke_command(
        self, command_path: str, command: str, output: str = "implicit", default=None
    ):
        try:
            command_object = self._app.get_commands().get_command_by_path(
                path=command_path.split(), return_first_executable=True
            )
            if command_object is None:
                raise AppModeException(
                    "Command not be found in config: " + command_path + " " + command
                )

            if (
                "args" in command_object
                and command_object.args.config.get("verbose", True)
                and command not in ["h", "cli_info"]
            ):
                print("Command: " + command_path + " " + command)

            return self._invoke_by_command_object(command_object, command, default)
        except (AppModeException, ToolsException):
            # todo: implement verbose version print(e)
            if command in ["h", "cli_info"]:
                return default
            return self._invoke_shell(command_path + " " + command, output)
        except Exception:
            # todo: implement verbose version print(e)
            return self._invoke_shell(command_path + " " + command, output)

    def _invoke_by_command_object(self, command: Command, method: str, default=None):
        if command is None:
            raise AppModeException("Could not invoke empty command")

        command_builder_factory = self._app.get_command_builder_factory()
        command_object = command_builder_factory.create(command).build(command)

        if hasattr(command_object, method):
            method_obj = getattr(command_object, method)
            result = method_obj()
            return result

        raise AppModeException("The command was not invocable on command object")

    def _invoke_shell(self, command: str, output: str = "implicit"):
        try:
            full_command = self.get_full_shell_command(command)
            command_runner = self._create_shell_command_runner_object(
                full_command, output
            )
            return command_runner()
        except Exception as e:
            self._app.logger.warning(e)
            return 0

    def _create_shell_command_runner_object(
        self, command: str, output: str = "implicit"
    ) -> CommandRunner:
        command_data = {
            Command.Constants.TYPE: Command.Constants.TYPES.CLI,
            Command.Constants.ARGS: {
                CommandArgs.Constants.COMMAND: command,
                CommandArgs.Constants.CWD: self._app.get_working_directory(),
                CommandArgs.Constants.COMMAND_CONFIG: {"output": output},
            },
        }
        return CommandRunner(
            Command("shell", command_data),
            {},
            command_input_reader_factory=self._app.get_object_manager().provide(
                ParametersReader.Factory
            ),
        )

    def _print_command_result(self, returned_value=None):
        if returned_value is None:
            return

        if type(returned_value) is list:
            for key in returned_value:
                print(key)
            return

        if type(returned_value) is int:
            if returned_value == 0:
                print(self._app.__.green("Done"))
            else:
                print(self._app.__.red("With errors"))
