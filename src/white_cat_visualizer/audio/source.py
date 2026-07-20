from __future__ import annotations

from typing import Protocol

from white_cat_visualizer.audio.frame import AudioFrame


class AudioSource(Protocol):
    @property
    def source_id(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    def reset(self) -> None: ...

    def next_frame(self) -> AudioFrame: ...
