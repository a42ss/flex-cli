from typing import Type
from typing import TypeVar, Generic
from pinject.object_graph import ObjectGraph
from ..object_manager import Factory as ObjectManagerFactory

T = TypeVar('T')


class Factory(Generic[T]):
    object_manager: ObjectGraph = None

    def __init__(self, uses_object_manager=True):
        if uses_object_manager and Factory.object_manager is None and ObjectManagerFactory.object_manager is not None:
            Factory.object_manager = ObjectManagerFactory.object_manager
        self.uses_object_manager = uses_object_manager

    def create(self, class_name: Type[T], data: dict = None) -> Generic[T]:
        has_exception = False
        if self.uses_object_manager is True:
            try:
                current_object = self.object_manager.provide(class_name)
            except Exception:
                has_exception = True

        if has_exception is True or self.uses_object_manager is False:
            current_object = class_name()

        if data is not None:
            for key, value in data.items():
                setattr(current_object, key, value)

        return current_object
