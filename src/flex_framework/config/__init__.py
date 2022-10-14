import pinject

from .deployment import Deployment


class ObjectManagerSpec(pinject.BindingSpec):
    deployment_config: Deployment
    arguments: dict

    def __init__(self, deployment_config: Deployment):
        self.deployment_config = deployment_config

    def provide_deployment(self):
        return self.deployment_config

    def configure(self, bind):
        bind(
            'deployment_config',
            in_scope=pinject.SINGLETON,
            annotated_with='flex_framework.config.deployment',
            to_instance=self.deployment_config
        )
