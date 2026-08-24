from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol

from white_cat_visualizer.audio.frame import AudioFrame


class AudioSource(Protocol):
    @property
    def source_id(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    def reset(self) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def next_frame(self) -> AudioFrame: ...


AudioSourceProvider = Callable[[], Sequence[AudioSource]]
