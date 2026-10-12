from __future__ import annotations

import pytest

from evaligator.core.errors import DuplicateRegistrationError, EvaligatorError
from evaligator.core.registry import Registry


class Thing:
    pass


def test_register_and_get_round_trip() -> None:
    registry: Registry[Thing] = Registry("thing")

    @registry.register("thing")
    class Registered(Thing):
        pass

    assert registry.get("thing") is Registered
    assert registry.names() == ["thing"]
    assert "thing" in registry
    assert len(registry) == 1
    assert list(registry) == ["thing"]


def test_get_unknown_name_raises_with_known_names() -> None:
    registry: Registry[Thing] = Registry("thing")
    registry.register("known")(Thing)
    with pytest.raises(EvaligatorError, match="known"):
        registry.get("missing")


def test_duplicate_registration_raises() -> None:
    registry: Registry[Thing] = Registry("thing")
    registry.register("thing")(Thing)
    with pytest.raises(DuplicateRegistrationError):
        registry.register("thing")(Thing)
