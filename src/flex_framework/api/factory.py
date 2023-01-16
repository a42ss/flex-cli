from typing import Generic, Optional, Type, TypeVar

from pinject.object_graph import ObjectGraph

from ..exceptions import FactoryException, ObjectManagerException
from ..object_manager import Factory as ObjectManagerFactory


T = TypeVar("T")


class Factory(Generic[T]):
    object_manager: ObjectGraph = None

    def __init__(self, uses_object_manager=True):
        if (
            uses_object_manager
            and Factory.object_manager is None
            and ObjectManagerFactory.object_manager is not None
        ):
            Factory.object_manager = ObjectManagerFactory.object_manager
        self.uses_object_manager = uses_object_manager

    def create(self, class_name: Type[T], data: Optional[dict] = None) -> T:
        try:
            if self.uses_object_manager is True:
                try:
                    current_object = self.object_manager.provide(class_name)
                except ObjectManagerException:
                    current_object = class_name()
            else:
                current_object = class_name()
        except ObjectManagerException:
            raise FactoryException("Object creation failed for: " + str(class_name))

        if data is not None:
            for key, value in data.items():
                setattr(current_object, key, value)

        return current_object
