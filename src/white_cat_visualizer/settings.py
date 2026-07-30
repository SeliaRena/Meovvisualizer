from __future__ import annotations

import json
import math
import os
import warnings
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from PySide6.QtCore import Property, QObject, Slot

if TYPE_CHECKING:
    from white_cat_visualizer.presentation.visualizer_controller import VisualizerController


DEFAULT_MARQUEE_PIXELS_PER_SECOND = 150
MINIMUM_MARQUEE_PIXELS_PER_SECOND = 50
MAXIMUM_MARQUEE_PIXELS_PER_SECOND = 1000
MARQUEE_PIXELS_PER_SECOND_STEP = 50
DEFAULT_WINDOW_ALWAYS_ON_TOP = True


def _parse_bool_setting(value: object, *, default: bool) -> tuple[bool, bool]:
    if isinstance(value, bool):
        return value, True
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True, True
        if normalized == "false":
            return False, True
    return default, False


def _normalize_marquee_speed(value: object) -> tuple[int, bool]:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return DEFAULT_MARQUEE_PIXELS_PER_SECOND, False
    try:
        numeric_value = float(value)
    except (ValueError, OverflowError):
        return DEFAULT_MARQUEE_PIXELS_PER_SECOND, False
    if not math.isfinite(numeric_value):
        return DEFAULT_MARQUEE_PIXELS_PER_SECOND, False

    clamped_value = min(
        max(numeric_value, MINIMUM_MARQUEE_PIXELS_PER_SECOND),
        MAXIMUM_MARQUEE_PIXELS_PER_SECOND,
    )
    snapped_steps = math.floor(clamped_value / MARQUEE_PIXELS_PER_SECOND_STEP + 0.5)
    snapped_value = snapped_steps * MARQUEE_PIXELS_PER_SECOND_STEP
    return snapped_value, True


@dataclass(frozen=True, slots=True)
class WindowSettings:
    x: int | None = None
    y: int | None = None
    width: int = 960
    height: int = 720


@dataclass(frozen=True, slots=True)
class ApplicationSettings:
    source_id: str | None = None
    mode: str = "Reference bars"
    sensitivity: float = 1.0
    window: WindowSettings = WindowSettings()
    window_always_on_top: bool = DEFAULT_WINDOW_ALWAYS_ON_TOP
    marquee_pixels_per_second: int = DEFAULT_MARQUEE_PIXELS_PER_SECOND


class SettingsStore(Protocol):
    def load(self) -> ApplicationSettings: ...

    def save(self, settings: ApplicationSettings) -> bool: ...


def default_settings_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "WhiteCatVisualizer" / "settings.json"
    return Path.home() / ".config" / "white-cat-visualizer" / "settings.json"


class JsonSettingsStore:
    """Small JSON adapter with validated reads and explicit fallback warnings."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> ApplicationSettings:
        try:
            text = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ApplicationSettings()
        except OSError as error:
            self._warn(f"could not read settings: {error}; using defaults")
            return ApplicationSettings()

        try:
            raw_value = json.loads(text)
        except json.JSONDecodeError as error:
            self._warn(f"settings JSON is invalid: {error.msg}; using defaults")
            return ApplicationSettings()

        if not isinstance(raw_value, dict):
            self._warn("settings root is not an object; using defaults")
            return ApplicationSettings()

        raw = cast(dict[str, object], raw_value)
        defaults = ApplicationSettings()
        invalid_fields: list[str] = []

        source_value = raw.get("source_id")
        source_id = source_value if isinstance(source_value, str) and source_value else None
        if source_value is not None and source_id is None:
            invalid_fields.append("source_id")

        mode_value = raw.get("mode", defaults.mode)
        mode = mode_value if isinstance(mode_value, str) and mode_value else defaults.mode
        if mode == defaults.mode and mode_value != defaults.mode:
            invalid_fields.append("mode")

        sensitivity_value = raw.get("sensitivity", defaults.sensitivity)
        sensitivity = defaults.sensitivity
        if (
            isinstance(sensitivity_value, (int, float))
            and not isinstance(sensitivity_value, bool)
            and math.isfinite(sensitivity_value)
            and 0.5 <= sensitivity_value <= 2.0
        ):
            sensitivity = float(sensitivity_value)
        elif sensitivity_value != defaults.sensitivity:
            invalid_fields.append("sensitivity")

        window = self._load_window(raw.get("window"), invalid_fields)
        window_always_on_top, valid_always_on_top = _parse_bool_setting(
            raw.get("window_always_on_top", defaults.window_always_on_top),
            default=defaults.window_always_on_top,
        )
        if not valid_always_on_top:
            invalid_fields.append("window_always_on_top")

        marquee_pixels_per_second, valid_marquee_speed = _normalize_marquee_speed(
            raw.get(
                "marquee_pixels_per_second",
                defaults.marquee_pixels_per_second,
            )
        )
        if not valid_marquee_speed:
            invalid_fields.append("marquee_pixels_per_second")

        if invalid_fields:
            fields = ", ".join(invalid_fields)
            self._warn(f"invalid settings fields ({fields}); using defaults for those fields")
        return ApplicationSettings(
            source_id=source_id,
            mode=mode,
            sensitivity=sensitivity,
            window=window,
            window_always_on_top=window_always_on_top,
            marquee_pixels_per_second=marquee_pixels_per_second,
        )

    def save(self, settings: ApplicationSettings) -> bool:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(asdict(settings), indent=2, sort_keys=True) + "\n"
            self._path.write_text(payload, encoding="utf-8")
        except OSError as error:
            self._warn(f"could not save settings: {error}; current session will continue")
            return False
        return True

    @staticmethod
    def _load_window(raw_value: object, invalid_fields: list[str]) -> WindowSettings:
        defaults = WindowSettings()
        if raw_value is None:
            return defaults
        if not isinstance(raw_value, dict):
            invalid_fields.append("window")
            return defaults

        raw = cast(dict[str, object], raw_value)
        x = JsonSettingsStore._optional_int(raw.get("x"), "window.x", invalid_fields)
        y = JsonSettingsStore._optional_int(raw.get("y"), "window.y", invalid_fields)
        width = JsonSettingsStore._bounded_int(
            raw.get("width", defaults.width),
            minimum=520,
            default=defaults.width,
            field="window.width",
            invalid_fields=invalid_fields,
        )
        height = JsonSettingsStore._bounded_int(
            raw.get("height", defaults.height),
            minimum=480,
            default=defaults.height,
            field="window.height",
            invalid_fields=invalid_fields,
        )
        return WindowSettings(x=x, y=y, width=width, height=height)

    @staticmethod
    def _optional_int(value: object, field: str, invalid_fields: list[str]) -> int | None:
        if value is None:
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        invalid_fields.append(field)
        return None

    @staticmethod
    def _bounded_int(
        value: object,
        *,
        minimum: int,
        default: int,
        field: str,
        invalid_fields: list[str],
    ) -> int:
        if isinstance(value, int) and not isinstance(value, bool) and value >= minimum:
            return value
        invalid_fields.append(field)
        return default

    @staticmethod
    def _warn(message: str) -> None:
        warnings.warn(message, RuntimeWarning, stacklevel=3)


class SettingsManager(QObject):
    """Bridge validated settings to the controller and the QML window."""

    def __init__(
        self,
        store: SettingsStore | None = None,
        *,
        initial: ApplicationSettings | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._store = store
        self._settings = store.load() if store is not None else initial or ApplicationSettings()

    @property
    def settings(self) -> ApplicationSettings:
        return self._settings

    @Property(bool, constant=True)
    def hasWindowPosition(self) -> bool:
        return self._settings.window.x is not None and self._settings.window.y is not None

    @Property(int, constant=True)
    def windowX(self) -> int:
        return self._settings.window.x or 0

    @Property(int, constant=True)
    def windowY(self) -> int:
        return self._settings.window.y or 0

    @Property(int, constant=True)
    def windowWidth(self) -> int:
        return self._settings.window.width

    @Property(int, constant=True)
    def windowHeight(self) -> int:
        return self._settings.window.height

    @Property(bool, constant=True)
    def windowAlwaysOnTop(self) -> bool:
        return self._settings.window_always_on_top

    @Property(int, constant=True)
    def marqueePixelsPerSecond(self) -> int:
        return self._settings.marquee_pixels_per_second

    def watch_controller(self, controller: VisualizerController) -> None:
        controller.sourceChanged.connect(lambda: self._save_controller(controller))
        controller.modeChanged.connect(lambda: self._save_controller(controller))
        controller.sensitivityChanged.connect(lambda: self._save_controller(controller))

    @Slot(int, int, int, int)
    def saveWindow(self, x: int, y: int, width: int, height: int) -> None:
        window = WindowSettings(x=x, y=y, width=max(width, 520), height=max(height, 480))
        self._save_if_changed(replace(self._settings, window=window))

    @Slot(bool)
    def saveWindowAlwaysOnTop(self, value: bool) -> None:
        normalized, _ = _parse_bool_setting(
            value,
            default=DEFAULT_WINDOW_ALWAYS_ON_TOP,
        )
        self._save_if_changed(replace(self._settings, window_always_on_top=normalized))

    @Slot(float)
    def saveMarqueePixelsPerSecond(self, value: float) -> None:
        normalized, _ = _normalize_marquee_speed(value)
        self._save_if_changed(replace(self._settings, marquee_pixels_per_second=normalized))

    def _save_controller(self, controller: VisualizerController) -> None:
        self._save_if_changed(
            replace(
                self._settings,
                source_id=controller.sourceId,
                mode=controller.mode,
                sensitivity=controller.sensitivity,
            )
        )

    def _save_if_changed(self, settings: ApplicationSettings) -> None:
        if settings == self._settings:
            return
        self._settings = settings
        if self._store is not None:
            self._store.save(self._settings)
