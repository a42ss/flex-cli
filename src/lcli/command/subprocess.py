import json
import subprocess
from string import Template

import pinject

from lcli.command.exceptions import RequiredParameterException
from lcli.command.input import ParametersReader
from lcli.config import Command as ConfigCommand
from lcli.config import Config
from lcli.input.exctptions import InterruptedInputException


class CommandRunner:
    """
    Run a shell command using application configuration, and dynamic parameters reader
    """

    _command_input_reader_factory: ParametersReader.Factory
    _command: ConfigCommand
    _local_variables: Config

    @pinject.inject(all_except=["command", "local_variables"])
    def __init__(
        self,
        command: ConfigCommand,
        local_variables: dict,
        command_input_reader_factory: ParametersReader.Factory,
        parent_command: ConfigCommand = None,
    ):
        self._command_input_reader_factory = command_input_reader_factory
        self._command = command
        self._parent_command = parent_command
        self._local_variables = Config(local_variables)

    def __call__(self, **args: str):
        try:
            command_input_reader = self._command_input_reader_factory.create(
                self._command.args.params, self._local_variables
            )
            answers = command_input_reader.read()
            command = ""
            if (
                self._parent_command is not None
                and self._parent_command.args is not None
            ):
                command += self._parent_command.args.get("commands_prefix", "")
            command += " " + self._command.args.command

            command = self.append_parameters_to_command(command, answers, args)
            output_type = self._command.args.config.get("output", "implicit")
            if "args" in args:
                command += " " + args["args"]

            cwd = self._command.args.get("cwd", ".")
            # print("Command [" + cwd + "]: " + command)

            if self._command.type == "bash-script":
                script = self._command.args.get("script")
                process = subprocess.Popen(script, shell=True, cwd=cwd)
                process.communicate()
                return

            if self._command.name == "cli_info":
                output_type = "list"

            if output_type is None or output_type == "implicit":
                process = subprocess.Popen(command, shell=True, cwd=cwd)
                process.communicate()
                return

            if output_type == "list":
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                out, err = process.communicate()
                if process.returncode != 0:
                    return []

                processed_out = str(out.rstrip().decode())
                list_parts = [
                    y for y in (x.strip() for x in processed_out.splitlines()) if y
                ]
                return list_parts

            if output_type == "json":
                p = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                out, err = p.communicate()
                if p.returncode == 0:
                    return json.loads(str(out.rstrip().decode()))
        except InterruptedInputException:
            return []
        except RequiredParameterException as e:
            print("Parameter " + e.parameter.name + "is required")
            return []

    def append_parameters_to_command(self, command: str, answers: dict, args: dict):
        params = self._command.args.params
        if params is not None:
            for param in params:
                param_object = params.get_param(param)
                param_name = param_object.name
                if param_name != "":
                    if param_name[1:] in args:
                        param_value = args[param_name[1:]]
                        if param_object.output_format is not None and len(
                            param_object.output_format
                        ):
                            value_template = Template(param_object.output_format)
                            command = command + value_template.substitute(
                                {"value": param_value, "name": param_name}
                            )
                        else:
                            command = (
                                command + " " + param_name + ' "' + param_value + '"'
                            )
                        continue

                answer_list = [command]

                answer_output = ""
                if param_object.output_format is not None and len(
                    param_object.output_format
                ):
                    if param in answers:
                        value_template = Template(param_object.output_format)
                        answer_output = value_template.substitute(
                            {"value": answers[param], "name": param_name}
                        )
                else:
                    if param in answers:
                        answer_output = answers[param]

                answer_list.append(answer_output)

                command = " ".join(answer_list)

        command_template = Template(command)
        processed_local_variables = {}
        local_variables = self._local_variables.get_all()
        for key in local_variables:
            if type(local_variables[key]) in [dict]:
                string_param = ""
                for param_key in local_variables[key]:
                    for variable_value in local_variables[key][param_key]:
                        if len(string_param):
                            string_param += " "
                        string_param += param_key + " " + variable_value
                processed_local_variables[key] = string_param
                continue

            if type(local_variables[key]) in [list]:
                string_param = ""
                for index in local_variables[key]:
                    string_param += " " + local_variables[key][index]
                processed_local_variables[key] = string_param
                continue

            processed_local_variables[key] = local_variables[key]

        command = command_template.substitute(**processed_local_variables)

        return command

    @classmethod
    def parse_args(cls, arg_string: str):
        import argparse

        parser = argparse.ArgumentParser(description="Argparse Test script")
        parser.add_argument("-json", action="store_true")

        args = parser.parse_args(arg_string.split())
        return args
