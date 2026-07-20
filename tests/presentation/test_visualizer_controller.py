from __future__ import annotations

import pytest

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode

presentation = pytest.importorskip("white_cat_visualizer.presentation")
VisualizerController = presentation.VisualizerController


def make_controller(
    initial_mode: SyntheticMode = SyntheticMode.BASS_PULSE,
) -> VisualizerController:
    sources = tuple(SyntheticAudioSource(mode) for mode in SyntheticMode)
    return VisualizerController(
        sources,
        SpectrumAnalyzer(),
        initial_source_id=f"synthetic:{initial_mode.value}",
    )


def source_name(mode: SyntheticMode) -> str:
    return SyntheticAudioSource(mode).display_name


def test_controller_starts_with_deterministic_render_ready_state() -> None:
    controller = make_controller()

    assert controller.sourceNames == [source_name(mode) for mode in SyntheticMode]
    assert controller.source == source_name(SyntheticMode.BASS_PULSE)
    assert controller.modeNames == ["Reference bars"]
    assert controller.mode == "Reference bars"
    assert controller.sensitivity == 1.0
    assert controller.running is False
    assert controller.rms == 0.0
    assert controller.peak == 0.0
    assert controller.bands == [0.0] * 24
    assert controller.error == ""


def test_start_stop_and_restart_reset_the_pipeline_deterministically() -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)

    controller.toggleRunning()
    first_bands = controller.bands
    first_rms = controller.rms
    first_peak = controller.peak
    controller.processNextFrame()

    assert controller.running is True
    assert controller.bands != first_bands

    controller.toggleRunning()

    assert controller.running is False
    assert controller.bands == [0.0] * 24
    assert controller.rms == 0.0
    assert controller.peak == 0.0

    controller.toggleRunning()

    assert controller.bands == first_bands
    assert controller.rms == first_rms
    assert controller.peak == first_peak


def test_source_change_resets_analysis_and_publishes_selected_source() -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)
    controller.toggleRunning()
    noise_bands = controller.bands

    controller.source = source_name(SyntheticMode.SILENCE)

    assert controller.running is True
    assert controller.bands == [0.0] * 24
    assert controller.rms == 0.0
    assert controller.peak == 0.0

    controller.source = source_name(SyntheticMode.SEEDED_NOISE)

    assert controller.bands == noise_bands


def test_sensitivity_scales_the_latest_render_values_in_python() -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)
    controller.toggleRunning()
    bands = controller.bands
    rms = controller.rms
    peak = controller.peak

    controller.sensitivity = 2.0

    assert controller.bands == [min(value * 2.0, 1.0) for value in bands]
    assert controller.rms == min(rms * 2.0, 1.0)
    assert controller.peak == min(peak * 2.0, 1.0)


def test_sensitivity_is_clamped() -> None:
    controller = make_controller()

    controller.sensitivity = 5.0
    assert controller.sensitivity == 2.0

    controller.sensitivity = 0.0
    assert controller.sensitivity == 0.5
