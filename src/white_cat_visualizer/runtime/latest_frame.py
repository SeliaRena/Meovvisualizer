from __future__ import annotations

from threading import Lock
from typing import Generic, TypeVar

FrameT = TypeVar("FrameT")


class LatestFrameSlot(Generic[FrameT]):
    """Thread-safe single-value storage that replaces stale pending data."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._value: FrameT | None = None
        self._replacement_count = 0

    @property
    def capacity(self) -> int:
        return 1

    @property
    def pending_count(self) -> int:
        with self._lock:
            return int(self._value is not None)

    @property
    def replacement_count(self) -> int:
        with self._lock:
            return self._replacement_count

    def publish(self, value: FrameT) -> bool:
        """Store value and return whether an empty slot became occupied."""
        with self._lock:
            should_notify = self._value is None
            if not should_notify:
                self._replacement_count += 1
            self._value = value
            return should_notify

    def take(self) -> FrameT | None:
        with self._lock:
            value = self._value
            self._value = None
            return value

    def clear(self) -> None:
        with self._lock:
            self._value = None

    def reset_statistics(self) -> None:
        with self._lock:
            self._replacement_count = 0
