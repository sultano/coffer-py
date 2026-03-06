from __future__ import annotations

import copy
import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, TypeVar

import yaml

T = TypeVar("T")

_MISSING = object()

_BOOL_TRUE = frozenset({"true", "1", "yes"})
_BOOL_FALSE = frozenset({"false", "0", "no"})


class CofferError(Exception):
    """Base exception for all coffer errors."""


class Config(Mapping[str, Any]):
    """Typed config reader for resolved Coffer config files.

    Supports dot-notation for nested access (e.g. ``config.get("database.host")``).

    Note: keys containing literal dots are not accessible via dot-notation.
    Use ``config.to_dict()`` to access them directly if needed.

    Thread safety: ``Config`` instances are effectively immutable after construction.
    The internal data is deep-copied on creation, and no mutation methods are exposed.
    This makes ``Config`` safe to share across threads without synchronization.
    """

    __slots__ = ("_data",)

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = copy.deepcopy(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Create a Config from a dictionary.

        This is the preferred factory when constructing from code or test data.
        The input dict is deep-copied, so later mutations do not affect the Config.
        """
        return cls(data)

    @classmethod
    def from_file(cls, path: str | Path) -> Config:
        path = Path(path)
        ext = path.suffix.lower()

        if ext not in (".json", ".yaml", ".yml"):
            raise CofferError(f"Unsupported file extension: {ext}")

        try:
            text = path.read_text()
        except OSError as e:
            raise CofferError(f"Cannot read file: {e}") from e

        try:
            if ext == ".json":
                data = json.loads(text)
            else:
                data = yaml.safe_load(text)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise CofferError(f"Failed to parse {path.name}: {e}") from e

        if data is None:
            raise CofferError("Config file is empty")

        if not isinstance(data, dict):
            raise CofferError(
                f"Config file must contain a mapping at the root, got {type(data).__name__}"
            )

        return cls(data)

    def get(  # type: ignore[override]
        self, key: str, *, default: Any = _MISSING, type: type[T] | None = None
    ) -> Any:
        try:
            value = self._traverse(key)
        except KeyError:
            if default is _MISSING:
                raise
            value = default

        if type is not None:
            value = _coerce(value, type, key)

        if isinstance(value, dict):
            return Config(value)
        return value

    def __getitem__(self, key: str) -> Any:
        value = self._traverse(key)
        if isinstance(value, dict):
            return Config(value)
        return value

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        try:
            self._traverse(key)
            return True
        except KeyError:
            return False

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Config({self._data!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return self._data == other._data

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)

    def _traverse(self, key: str) -> Any:
        parts = key.split(".")
        current: Any = self._data
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(key)
            current = current[part]
        return current


def _coerce(value: Any, tp: type[Any], key: str) -> Any:
    if tp is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value == 1:
                return True
            if value == 0:
                return False
        if isinstance(value, str):
            low = value.lower()
            if low in _BOOL_TRUE:
                return True
            if low in _BOOL_FALSE:
                return False
        raise TypeError(f"Cannot coerce {value!r} to bool for key '{key}'")

    if tp is list:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",")]
        raise TypeError(f"Cannot coerce {value!r} to list for key '{key}'")

    try:
        return tp(value)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot coerce {value!r} to {tp.__name__} for key '{key}'") from e
