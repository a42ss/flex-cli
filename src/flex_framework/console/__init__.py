import pinject

from .input import Input


class ObjectManagerSpec(pinject.BindingSpec):
    def configure(self, bind):
        bind(
            "console_input",
            in_scope=pinject.SINGLETON,
            annotated_with="flex_framework.console.input.Input",
            to_instance=Input({"handler_arguments": {"positional": False}}),
        )
