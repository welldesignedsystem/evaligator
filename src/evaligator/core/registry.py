from __future__ import annotations

from collections.abc import Callable, Iterator

from evaligator.core.errors import DuplicateRegistrationError, EvaligatorError


class Registry[T]:
    """A name -> class registry backing plugin/entry-point discovery."""

    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: dict[str, type[T]] = {}

    def register(self, name: str) -> Callable[[type[T]], type[T]]:
        def decorator(cls: type[T]) -> type[T]:
            if name in self._items:
                raise DuplicateRegistrationError(f"{self._kind} {name!r} is already registered")
            self._items[name] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[T]:
        if name not in self._items:
            known = ", ".join(sorted(self._items)) or "<none>"
            raise EvaligatorError(f"unknown {self._kind} {name!r}; known: {known}")
        return self._items[name]

    def names(self) -> list[str]:
        return sorted(self._items)

    def __contains__(self, name: object) -> bool:
        return name in self._items

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())

    def __len__(self) -> int:
        return len(self._items)
