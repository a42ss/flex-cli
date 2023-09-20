from __future__ import annotations

from types import ModuleType
from typing import List

from pinject import BindingSpec

from ..model import Config
from .directories import DirectoriesConfig


class Deployment(Config):
    @property
    def dirs(self) -> DirectoriesConfig:
        return DirectoriesConfig(self.get("dirs", {}))

    @property
    def di_modules(self) -> List[ModuleType]:
        return self.get("di/modules", [])

    @property
    def di(self) -> DiConfig:
        return DiConfig(self.get("di", []))

    @property
    def input(self) -> dict:
        return self.get("input", {})

    @property
    def di_classes(self) -> List[type]:
        return self.get("di/classes", [])

    @property
    def di_binding_specs(self) -> List[BindingSpec]:
        binding_specs = self.get("di/binding_specs", [])
        binding_specs_objects: List[BindingSpec] = []
        for binding_spec in binding_specs:
            if callable(binding_spec):
                binding_spec_object = binding_spec(self)
                binding_specs_objects.append(binding_spec_object)
        return binding_specs_objects


class DiConfig(Deployment):
    @property
    def classes(self) -> List[type]:
        return self.get("classes", [])

    @property
    def modules(self) -> List[ModuleType]:
        return self.get("modules", [])
