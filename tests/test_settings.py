from __future__ import annotations

import json
from pathlib import Path

import pytest

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode
from white_cat_visualizer.presentation import VisualizerController
from white_cat_visualizer.settings import (
    ApplicationSettings,
    JsonSettingsStore,
    SettingsManager,
    WindowSettings,
)


def test_settings_round_trip_all_persisted_values(tmp_path: Path) -> None:
    store = JsonSettingsStore(tmp_path / "settings.json")
    expected = ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Long cats",
        sensitivity=1.7,
        window=WindowSettings(x=120, y=80, width=1280, height=800),
    )

    assert store.save(expected) is True

    assert store.load() == expected


def test_invalid_settings_warn_and_fall_back_field_by_field(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "source_id": 42,
                "mode": "Long cats",
                "sensitivity": "loud",
                "window": {"x": "left", "y": 30, "width": 100, "height": 700},
            }
        ),
        encoding="utf-8",
    )

    with pytest.warns(RuntimeWarning, match="invalid settings fields"):
        settings = JsonSettingsStore(path).load()

    assert settings == ApplicationSettings(
        mode="Long cats",
        window=WindowSettings(y=30, width=960, height=700),
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
    controller.setProperty("mode", "Bouncing cats")
    controller.setProperty("sensitivity", 1.4)
    manager.saveWindow(50, 70, 1200, 760)

    assert store.load() == ApplicationSettings(
        source_id="synthetic:frequency-sweep",
        mode="Bouncing cats",
        sensitivity=1.4,
        window=WindowSettings(x=50, y=70, width=1200, height=760),
    )
    controller.shutdown()
