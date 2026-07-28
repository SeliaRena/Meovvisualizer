from __future__ import annotations

import os
from collections.abc import Callable, Iterator

import pytest

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.frame import AudioFrame
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_core = pytest.importorskip("PySide6.QtCore")
qt_gui = pytest.importorskip("PySide6.QtGui")
presentation = pytest.importorskip("white_cat_visualizer.presentation")
ControllerErrorCode = presentation.ControllerErrorCode
VisualizerController = presentation.VisualizerController
QEventLoop = qt_core.QEventLoop
QTimer = qt_core.QTimer
QGuiApplication = qt_gui.QGuiApplication


@pytest.fixture(scope="module")
def application() -> QGuiApplication:
    existing = QGuiApplication.instance()
    return existing if isinstance(existing, QGuiApplication) else QGuiApplication([])


@pytest.fixture
def make_controller() -> Iterator[Callable[..., VisualizerController]]:
    controllers: list[VisualizerController] = []

    def factory(
        initial_mode: SyntheticMode = SyntheticMode.BASS_PULSE,
        analyzer: SpectrumAnalyzer | None = None,
    ) -> VisualizerController:
        sources = tuple(SyntheticAudioSource(mode) for mode in SyntheticMode)
        controller = VisualizerController(
            sources,
            SpectrumAnalyzer() if analyzer is None else analyzer,
            initial_source_id=f"synthetic:{initial_mode.value}",
        )
        controllers.append(controller)
        return controller

    yield factory
    for controller in controllers:
        controller.shutdown()


def wait_until(predicate: Callable[[], bool]) -> None:
    if predicate():
        return

    loop = QEventLoop()
    poll_timer = QTimer()
    poll_timer.setInterval(0)
    poll_timer.timeout.connect(lambda: loop.quit() if predicate() else None)
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.timeout.connect(loop.quit)
    poll_timer.start()
    timeout_timer.start(1_000)
    loop.exec()
    poll_timer.stop()
    timed_out = not timeout_timer.isActive()
    timeout_timer.stop()

    assert not timed_out, "runtime update was not delivered"
    assert predicate()


def source_name(mode: SyntheticMode) -> str:
    return SyntheticAudioSource(mode).display_name


def test_controller_starts_with_deterministic_render_ready_state(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller()

    assert controller.sourceNames == [source_name(mode) for mode in SyntheticMode]
    assert controller.source == source_name(SyntheticMode.BASS_PULSE)
    assert controller.modeNames == ["Reference bars", "Long cats"]
    assert controller.mode == "Reference bars"
    assert controller.sensitivity == 1.0
    assert controller.running is False
    assert controller.rms == 0.0
    assert controller.peak == 0.0
    assert controller.bands == [0.0] * 24
    assert controller.error == ""
    assert controller.errorCode == ""
    assert controller.error_state is None
    assert controller.debugOverlayEnabled is False
    assert controller.framesPerSecond == 0.0
    assert controller.processingTimeMs == 0.0
    assert controller.replacedFrames == 0


def test_controller_accepts_persisted_release_preferences() -> None:
    sources = tuple(SyntheticAudioSource(mode) for mode in SyntheticMode)
    controller = VisualizerController(
        sources,
        SpectrumAnalyzer(),
        initial_source_id="synthetic:frequency-sweep",
        initial_mode="Long cats",
        initial_sensitivity=1.6,
    )

    assert controller.sourceId == "synthetic:frequency-sweep"
    assert controller.mode == "Long cats"
    assert controller.sensitivity == 1.6

    controller.shutdown()


def test_controller_accepts_only_documented_visualizer_modes(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller()

    controller.mode = "Long cats"
    assert controller.mode == "Long cats"

    controller.mode = "Unknown mode"
    assert controller.mode == "Long cats"


def test_start_stop_and_restart_reset_the_pipeline_deterministically(
    application: QGuiApplication,
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)

    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))
    first_bands = controller.bands
    first_rms = controller.rms
    first_peak = controller.peak

    assert controller.running is True

    controller.toggleRunning()

    assert controller.running is False
    assert controller.bands == [0.0] * 24
    assert controller.rms == 0.0
    assert controller.peak == 0.0

    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))

    assert controller.bands == first_bands
    assert controller.rms == first_rms
    assert controller.peak == first_peak
    application.processEvents()


def test_source_change_resets_analysis_and_publishes_selected_source(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))
    noise_bands = controller.bands

    controller.source = source_name(SyntheticMode.SILENCE)

    assert controller.running is True
    assert controller.bands == [0.0] * 24
    assert controller.rms == 0.0
    assert controller.peak == 0.0

    controller.source = source_name(SyntheticMode.SEEDED_NOISE)
    wait_until(lambda: any(controller.bands))

    assert controller.bands == noise_bands


def test_sensitivity_scales_the_latest_render_values_in_python(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))
    bands = controller.bands
    rms = controller.rms
    peak = controller.peak

    controller.sensitivity = 2.0

    assert controller.bands == [min(value * 2.0, 1.0) for value in bands]
    assert controller.rms == min(rms * 2.0, 1.0)
    assert controller.peak == min(peak * 2.0, 1.0)


def test_sensitivity_is_clamped(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller()

    controller.sensitivity = 5.0
    assert controller.sensitivity == 2.0

    controller.sensitivity = 0.0
    assert controller.sensitivity == 0.5


class FailingAnalyzer(SpectrumAnalyzer):
    def analyze(self, frame: AudioFrame) -> VisualizerFrame:
        raise RuntimeError(f"failed on frame {frame.frame_index}")


def test_worker_failure_becomes_typed_controller_error_state(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller(analyzer=FailingAnalyzer())

    controller.toggleRunning()
    wait_until(lambda: controller.error_state is not None)

    assert controller.running is False
    assert controller.errorCode == ControllerErrorCode.ANALYSIS_WORKER_FAILED.value
    assert controller.error_state.code is ControllerErrorCode.ANALYSIS_WORKER_FAILED
    assert "RuntimeError" in controller.error
    assert controller.bands == [0.0] * 24


def test_stopped_controller_ignores_queued_runtime_delivery(
    application: QGuiApplication,
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))

    controller.toggleRunning()
    controller.processNextFrame()
    application.processEvents()

    assert controller.running is False
    assert controller.bands == [0.0] * 24
    assert controller.rms == 0.0
    assert controller.peak == 0.0


def test_debug_overlay_is_opt_in_and_runtime_diagnostics_are_bounded(
    make_controller: Callable[..., VisualizerController],
) -> None:
    controller = make_controller(SyntheticMode.SEEDED_NOISE)

    controller.debugOverlayEnabled = True
    controller.toggleRunning()
    wait_until(lambda: controller.processingTimeMs > 0.0)

    assert controller.debugOverlayEnabled is True
    assert controller.framesPerSecond >= 0.0
    assert controller.processingTimeMs > 0.0
    assert controller.replacedFrames >= 0
