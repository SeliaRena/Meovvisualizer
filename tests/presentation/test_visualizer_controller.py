from __future__ import annotations

import pytest

presentation = pytest.importorskip("white_cat_visualizer.presentation")
VisualizerController = presentation.VisualizerController


def test_controller_starts_with_static_render_ready_state() -> None:
    controller = VisualizerController()

    assert controller.source in controller.sourceNames
    assert controller.mode in controller.modeNames
    assert controller.sensitivity == 1.0
    assert controller.running is False
    assert controller.rms == 0.0
    assert controller.peak == 0.0
    assert controller.bands == [0.0] * 24
    assert controller.error == ""


def test_controller_owns_mutable_control_state() -> None:
    controller = VisualizerController()

    controller.mode = controller.modeNames[1]
    controller.sensitivity = 5.0
    controller.toggleRunning()

    assert controller.mode == "Bouncing cat heads"
    assert controller.sensitivity == 2.0
    assert controller.running is True
