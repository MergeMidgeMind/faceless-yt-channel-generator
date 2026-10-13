"""Stage registry — maps stage names to classes for plugin-style loading."""
from __future__ import annotations

from typing import Type

from src.core.pipeline import Stage

_REGISTRY: dict[str, Type[Stage]] = {}


def register_stage(name: str):
    def deco(cls: Type[Stage]) -> Type[Stage]:
        _REGISTRY[name] = cls
        return cls
    return deco


def get_stage(name: str) -> Type[Stage]:
    if name not in _REGISTRY:
        raise KeyError(f"stage {name!r} not registered")
    return _REGISTRY[name]


def all_stages() -> dict[str, Type[Stage]]:
    return dict(_REGISTRY)