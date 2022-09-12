from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from lcli.input.exctptions import InterruptedInputException
from lcli.input.prompt_toolkit import input_dialog, radiolist_dialog


class AskQuestions(object):
    _questions: dict

    def __init__(self, questions: dict):
        self._questions = questions

    def ask(self):
        result = {}
        errors = []
        for key in self._questions:
            answer = None
            try:
                question = self._questions[key]
                if question["type"] == "list":
                    answer = self.ask_radio(question)

                if question["type"] == "autocomplete":
                    answer = self.ask_autocompleter(question)

                if question["type"] == "input":
                    answer = self.ask_text(question)
            except Exception as e:
                errors.append(e)

            if answer is None:
                raise InterruptedInputException(
                    "Input process was stopped", result, errors
                )

            result[key] = answer
        return result

    @classmethod
    def ask_radio(cls, question):
        choices = question["choices"]
        asked_choices = []
        if type(choices) == list:
            for choice in choices:
                asked_choices.append((choice, choice))
        if type(choices) == dict:
            for choice in choices:
                asked_choices.append((choice, choices[choice]))

        if len(asked_choices) == 0:
            asked_choices = [("N/A", "N/A")]
        buttons = {}
        if "buttons" in question:
            buttons = question["buttons"]

        result = radiolist_dialog(
            values=asked_choices,
            title=question["message"],
            text=question["message"],
            buttons=buttons,
        ).run()
        return result

    @classmethod
    def ask_autocompleter(cls, question):
        choices_completer = WordCompleter(
            question["choices"], ignore_case=True, sentence=True
        )
        # Key bindings.
        bindings = KeyBindings()

        @bindings.add(Keys.Escape)
        @bindings.add("c-c")
        @bindings.add("c-q")
        def _(event):
            """Pressing Ctrl-Q or Ctrl-C will exit the user interface."""
            event.app.exit()

        return prompt(
            question["message"],
            completer=choices_completer,
            complete_while_typing=False,
            key_bindings=bindings,
        )

    def ask_text(self, question):
        app = input_dialog(title=question["message"], text=question["message"])
        result = app.run()

        return result
