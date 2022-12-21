from typing import Generic, TypeVar

import pinject

from ..object_manager import ObjectManager


T = TypeVar("T")
S = TypeVar("S")


class ProxyContainer(Generic[S]):
    _subject: S

    def get_subject(self) -> S:
        return self._subject


class ProxyInterface(Generic[T, S]):
    _object_manager: ObjectManager
    _instance_class: object
    _shared: bool

    @pinject.annotate_arg("object_manager", "flex_framework.object_manager")
    def __init__(
        self, object_manager: ObjectManager, instance_class, shared: bool = True
    ):
        self._object_manager = object_manager
        self._instance_class = instance_class
        self._shared = shared

    def get_proxy_instance(self) -> ProxyContainer:
        return self._object_manager.provide(self._instance_class)

    def get_subject(self) -> S:
        return self.get_proxy_instance().get_subject()

    def __getattr__(self, method_name):
        def method(*args, **kwargs):
            subject = self.get_proxy_instance().get_subject()
            return getattr(subject, method_name)(*args, **kwargs)

        return method
