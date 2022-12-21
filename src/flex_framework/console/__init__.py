import pinject

from ..config import Deployment
from .input import Input


class ObjectManagerSpec(pinject.bindings.BindingSpec):

    deployment_config: Deployment

    def __init__(self, deployment_config: Deployment):
        self.deployment_config = deployment_config

    def configure(self, bind):
        bind(
            "console_input",
            in_scope=pinject.SINGLETON,
            annotated_with="flex_framework.console.input.Input",
            to_instance=Input({"handler_arguments": {"positional": False}}),
        )
