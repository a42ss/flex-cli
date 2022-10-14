from __future__ import annotations

import pinject

from flex_framework.config import Deployment


class ObjectManager(pinject.object_graph.ObjectGraph):
    @staticmethod
    def get_instance():
        return Factory.object_manager


class Factory:
    object_manager: ObjectManager | None = None

    def create(self, arguments: dict) -> ObjectManager:
        deployment_config = Deployment(arguments)

        import flex_framework.config
        import flex_framework.console.handler
        import flex_framework.environment
        import flex_framework.logger

        object_manager = pinject.new_object_graph(
            modules=[
                flex_framework.logger,
                flex_framework.environment,
                flex_framework.console.input,
                flex_framework.console.handler,
                flex_framework.config.deployment,
            ],
            binding_specs=[
                flex_framework.config.ObjectManagerSpec(deployment_config),
                flex_framework.console.ObjectManagerSpec(),
                flex_framework.logger.ObjectManagerSpec(deployment_config),
            ],
        )

        object_manager.__class__ = ObjectManager
        Factory.object_manager = object_manager
        if isinstance(object_manager, ObjectManager):
            return object_manager

        raise Exception("Unable to configure object manager")
