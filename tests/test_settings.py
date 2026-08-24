from __future__ import annotations

import json
from pathlib import Path

import pytest

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode
from white_cat_visualizer.presentation import VisualizerController
from white_cat_visualizer.settings import (
    DEFAULT_MARQUEE_PIXELS_PER_SECOND,
    MAXIMUM_MARQUEE_PIXELS_PER_SECOND,
    MINIMUM_MARQUEE_PIXELS_PER_SECOND,
    ApplicationSettings,
    JsonSettingsStore,
    SettingsManager,
    WindowSettings,
)


class CountingJsonSettingsStore(JsonSettingsStore):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.save_count = 0

    def save(self, settings: ApplicationSettings) -> bool:
        self.save_count += 1
        return super().save(settings)


def test_missing_settings_file_uses_defaults(tmp_path: Path) -> None:
    store = JsonSettingsStore(tmp_path / "settings.json")

    assert store.load() == ApplicationSettings()


def test_settings_round_trip_all_persisted_values(tmp_path: Path) -> None:
    store = JsonSettingsStore(tmp_path / "settings.json")
    expected = ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Long cats",
        sensitivity=1.7,
        window=WindowSettings(x=120, y=80, width=1280, height=800),
        window_always_on_top=False,
        marquee_pixels_per_second=750,
    )

    assert store.save(expected) is True

    reloaded_manager = SettingsManager(JsonSettingsStore(tmp_path / "settings.json"))
    assert reloaded_manager.settings == expected


def test_legacy_settings_without_new_fields_uses_new_defaults(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "source_id": "synthetic:frequency-sweep",
                "mode": "Long cats",
                "sensitivity": 1.4,
                "window": {"x": 10, "y": 20, "width": 1100, "height": 700},
            }
        ),
        encoding="utf-8",
    )

    assert JsonSettingsStore(path).load() == ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Long cats",
        sensitivity=1.4,
        window=WindowSettings(x=10, y=20, width=1100, height=700),
    )


def test_false_string_is_not_loaded_as_true(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps({"window_always_on_top": "false"}),
        encoding="utf-8",
    )

    assert JsonSettingsStore(path).load().window_always_on_top is False


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        (50, MINIMUM_MARQUEE_PIXELS_PER_SECOND),
        (74.9, 50),
        (75.0, 100),
        ("249.9", 250),
        (25, MINIMUM_MARQUEE_PIXELS_PER_SECOND),
        (1_500.0, MAXIMUM_MARQUEE_PIXELS_PER_SECOND),
    ],
)
def test_marquee_speed_clamps_and_snaps_valid_numbers(
    tmp_path: Path,
    raw_value: object,
    expected: int,
) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps({"marquee_pixels_per_second": raw_value}),
        encoding="utf-8",
    )

    assert JsonSettingsStore(path).load().marquee_pixels_per_second == expected


@pytest.mark.parametrize(
    "raw_value",
    [True, float("nan"), float("inf"), float("-inf"), "fast", ""],
)
def test_invalid_marquee_speed_falls_back_to_default(
    tmp_path: Path,
    raw_value: object,
) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps({"marquee_pixels_per_second": raw_value}),
        encoding="utf-8",
    )

    with pytest.warns(RuntimeWarning, match="marquee_pixels_per_second"):
        settings = JsonSettingsStore(path).load()

    assert settings.marquee_pixels_per_second == DEFAULT_MARQUEE_PIXELS_PER_SECOND


def test_one_invalid_new_field_preserves_every_other_valid_field(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "source_id": "synthetic:frequency-sweep",
                "mode": "Long cats",
                "sensitivity": 1.8,
                "window": {"x": 25, "y": 35, "width": 1200, "height": 800},
                "window_always_on_top": False,
                "marquee_pixels_per_second": "fast",
            }
        ),
        encoding="utf-8",
    )

    with pytest.warns(RuntimeWarning, match="marquee_pixels_per_second"):
        settings = JsonSettingsStore(path).load()

    assert settings == ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Long cats",
        sensitivity=1.8,
        window=WindowSettings(x=25, y=35, width=1200, height=800),
        window_always_on_top=False,
    )


def test_invalid_settings_warn_and_fall_back_field_by_field(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "source_id": 42,
                "mode": "Long cats",
                "sensitivity": "loud",
                "window": {"x": "left", "y": 30, "width": 100, "height": 700},
                "window_always_on_top": False,
                "marquee_pixels_per_second": 400,
            }
        ),
        encoding="utf-8",
    )

    with pytest.warns(RuntimeWarning, match="invalid settings fields"):
        settings = JsonSettingsStore(path).load()

    assert settings == ApplicationSettings(
        mode="Long cats",
        window=WindowSettings(y=30, width=960, height=700),
        window_always_on_top=False,
        marquee_pixels_per_second=400,
    )


def test_malformed_settings_file_uses_complete_defaults(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.warns(RuntimeWarning, match="using defaults"):
        settings = JsonSettingsStore(path).load()

    assert settings == ApplicationSettings()


def test_settings_write_failure_is_reported_without_raising(tmp_path: Path) -> None:
    occupied_parent = tmp_path / "not-a-directory"
    occupied_parent.write_text("occupied", encoding="utf-8")
    store = JsonSettingsStore(occupied_parent / "settings.json")

    with pytest.warns(RuntimeWarning, match="current session will continue"):
        saved = store.save(ApplicationSettings())

    assert saved is False


def test_manager_persists_controller_choices_and_window_geometry(tmp_path: Path) -> None:
    store = JsonSettingsStore(tmp_path / "settings.json")
    manager = SettingsManager(store)
    sources = tuple(SyntheticAudioSource(mode) for mode in SyntheticMode)
    controller = VisualizerController(sources, SpectrumAnalyzer())
    manager.watch_controller(controller)

    controller.setProperty(
        "source", SyntheticAudioSource(SyntheticMode.FREQUENCY_SWEEP).display_name
    )
    controller.setProperty("mode", "Long cats")
    controller.setProperty("sensitivity", 1.4)
    manager.saveWindowAlwaysOnTop(False)
    manager.saveMarqueePixelsPerSecond(625.0)
    manager.saveWindow(50, 70, 1200, 760)

    assert store.load() == ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Long cats",
        sensitivity=1.4,
        window=WindowSettings(x=50, y=70, width=1200, height=760),
        window_always_on_top=False,
        marquee_pixels_per_second=650,
    )
    controller.shutdown()


def test_new_setting_saves_preserve_existing_values(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    existing = ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Long cats",
        sensitivity=1.6,
        window=WindowSettings(x=40, y=60, width=1400, height=900),
    )
    assert JsonSettingsStore(path).save(existing) is True
    manager = SettingsManager(JsonSettingsStore(path))

    manager.saveWindowAlwaysOnTop(False)
    manager.saveMarqueePixelsPerSecond(525.0)

    assert JsonSettingsStore(path).load() == ApplicationSettings(
        source_id=existing.source_id,
        mode=existing.mode,
        sensitivity=existing.sensitivity,
        window=existing.window,
        window_always_on_top=False,
        marquee_pixels_per_second=550,
    )


def test_manager_does_not_save_unchanged_normalized_values(tmp_path: Path) -> None:
    store = CountingJsonSettingsStore(tmp_path / "settings.json")
    manager = SettingsManager(store)

    manager.saveWindowAlwaysOnTop(True)
    manager.saveMarqueePixelsPerSecond(149.0)

    assert store.save_count == 0

    manager.saveMarqueePixelsPerSecond(176.0)
    manager.saveMarqueePixelsPerSecond(200.0)

    assert store.save_count == 1
