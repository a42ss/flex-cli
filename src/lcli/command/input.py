import subprocess

from lcli.command.exceptions import RequiredParameterException
from lcli.config import CommandArgsParams, Config, ConfigException
from lcli.input.prompt import AskQuestions


class ParametersReader(object):
    _params: CommandArgsParams
    _defaults: Config

    class Factory(object):
        @classmethod
        def create(
            cls, params: CommandArgsParams, defaults: Config
        ) -> "ParametersReader":
            return ParametersReader(params, defaults)

    def __init__(self, params: CommandArgsParams, defaults: Config):
        self._defaults = defaults
        self._params = params

    def read(self):

        if self._params is not None:
            questions = {}
            answers = {}
            for param in self._params:
                param_object = self._params.get_param(param)

                if param_object.type == "config":
                    try:
                        answers[param] = self._defaults.get(
                            param_object.get("config_path")
                        )
                    except ConfigException:
                        if param_object.get("required", False):
                            raise RequiredParameterException(param_object)
                        continue

                if param_object.type == "input":
                    questions[param] = {
                        "type": "input",
                        "name": param,
                        "message": param_object.message,
                    }

                if param_object.type == "list" or param_object.type == "autocomplete":
                    question = param_object.get_all().copy()
                    question["name"] = param
                    if (
                        param_object.choices_cmd is not None
                        and not param_object.choices_cmd.is_empty()
                    ):
                        choices_cmd = param_object.choices_cmd
                        stdout = subprocess.check_output(choices_cmd.command.split())
                        out = stdout.decode()
                        choices_result = [
                            b.strip(choices_cmd.filter["strip"])
                            for b in out.splitlines()
                        ]
                        question["choices"] = choices_result
                    else:
                        question["choices"] = {}
                        if param_object.choices is not None:
                            for k in param_object.choices.get_all():
                                choice = param_object.choices.get_choice(k)
                                question["choices"][choice.value] = choice.name
                    question["answers"] = {}
                    question["type"] = "autocomplete"
                    questions[param] = question

            questions_object = AskQuestions(questions)
            qa = questions_object.ask()
            for q in qa:
                answers[q] = qa[q]
            return answers

        return {}
