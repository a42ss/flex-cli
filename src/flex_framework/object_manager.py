from __future__ import annotations

import pinject

from .config import Deployment


class ObjectManager(pinject.object_graph.ObjectGraph):
    @staticmethod
    def get_instance():
        return Factory.object_manager


class Factory:
    object_manager: ObjectManager | None = None

    def create(self, arguments: dict) -> ObjectManager:
        deployment_config = Deployment(arguments)

        object_manager = pinject.new_object_graph(
            modules=deployment_config.di.modules,
            binding_specs=deployment_config.di_binding_specs,
            classes=deployment_config.di.classes,
        )

        object_manager.__class__ = ObjectManager
        Factory.object_manager = object_manager
        if isinstance(object_manager, ObjectManager):
            return object_manager

        raise Exception("Unable to configure object manager")
