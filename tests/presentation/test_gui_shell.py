from __future__ import annotations

import os
from collections.abc import Callable

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from white_cat_visualizer.audio.frame import AudioFrame

qt_core = pytest.importorskip("PySide6.QtCore")
qt_gui = pytest.importorskip("PySide6.QtGui")
qt_quick = pytest.importorskip("PySide6.QtQuick")
application_module = pytest.importorskip("white_cat_visualizer.app")

QObject = qt_core.QObject
QColor = qt_gui.QColor
QGuiApplication = qt_gui.QGuiApplication
QQuickItem = qt_quick.QQuickItem
QEventLoop = qt_core.QEventLoop
QTimer = qt_core.QTimer
create_engine = application_module.create_engine
create_controller = application_module.create_controller
SpectrumAnalyzer = application_module.SpectrumAnalyzer
VisualizerController = application_module.VisualizerController


class RemovedAudioSource:
    @property
    def source_id(self) -> str:
        return "test:removed-output"

    @property
    def display_name(self) -> str:
        return "Removed output"

    def reset(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def next_frame(self) -> AudioFrame:
        raise OSError("selected output device was removed")


@pytest.fixture(scope="module")
def application() -> QGuiApplication:
    existing = QGuiApplication.instance()
    return existing if isinstance(existing, QGuiApplication) else QGuiApplication([])


def visualizer_delegates(row: QQuickItem, object_name: str) -> list[QQuickItem]:
    return [item for item in row.childItems() if item.property("objectName") == object_name]


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


def test_shell_loads_and_keeps_canvas_usable_at_supported_sizes(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    roots = engine.rootObjects()
    assert len(roots) == 1
    root = roots[0]

    for width, height in ((520, 480), (960, 720), (1440, 900)):
        root.setProperty("width", width)
        root.setProperty("height", height)
        application.processEvents()

        controls = root.findChild(QObject, "controlSurface")
        canvas = root.findChild(QObject, "visualizerCanvas")
        assert controls is not None
        assert canvas is not None
        assert canvas.property("height") >= 240
        assert controls.property("y") + controls.property("height") <= canvas.property("y")

    del engine


def test_shell_uses_documented_monochrome_dark_surfaces(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    theme = root.findChild(QObject, "themeTokens")
    controls = root.findChild(QObject, "controlSurface")
    canvas = root.findChild(QObject, "visualizerCanvas")

    assert theme is not None
    assert controls is not None
    assert canvas is not None
    assert root.property("color") == QColor("#0D0D0F")
    assert controls.property("color") == QColor("#161619")
    assert canvas.property("color") == QColor("#111113")
    assert theme.property("primaryText") == QColor("#F5F5F5")
    assert theme.property("border") == QColor("#303036")

    del engine


def test_release_diagnostics_overlay_is_off_by_default_and_opt_in(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    overlay = root.findChild(QObject, "diagnosticsOverlay")

    assert overlay is not None
    assert overlay.property("visible") is False

    controller.debugOverlayEnabled = True
    application.processEvents()

    assert overlay.property("visible") is True

    del engine


def test_shell_renders_all_fixed_visualizers_and_separate_levels(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    bars = root.findChild(QObject, "spectrumBars")
    long_cats = root.findChild(QObject, "longCatBars")
    bouncing_cats = root.findChild(QObject, "bouncingCatHeads")
    rms_level = root.findChild(QObject, "rmsLevel")
    peak_level = root.findChild(QObject, "peakLevel")

    assert bars is not None
    assert bars.property("count") == 24
    assert long_cats is not None
    assert long_cats.property("count") == 24
    assert bouncing_cats is not None
    assert bouncing_cats.property("count") == 24
    assert rms_level is not None
    assert peak_level is not None

    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))

    assert any(controller.bands)
    assert rms_level.property("value") == pytest.approx(controller.rms)
    assert peak_level.property("value") == pytest.approx(controller.peak)

    controller.toggleRunning()
    del engine


def test_shell_shows_audio_failures_without_backend_logic(
    application: QGuiApplication,
) -> None:
    controller = VisualizerController([RemovedAudioSource()], SpectrumAnalyzer())
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    source_error = root.findChild(QObject, "sourceError")

    assert source_error is not None
    assert source_error.property("visible") is False

    controller.toggleRunning()
    wait_until(lambda: bool(controller.error))
    application.processEvents()

    assert source_error.property("visible") is True
    assert "selected output device was removed" in source_error.property("text")

    del engine


def test_mode_switching_and_cat_mappings_are_deterministic(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    reference_view = root.findChild(QQuickItem, "referenceVisualizer")
    long_cat_view = root.findChild(QQuickItem, "longCatVisualizer")
    bouncing_cat_view = root.findChild(QQuickItem, "bouncingCatVisualizer")

    assert reference_view is not None
    assert long_cat_view is not None
    assert bouncing_cat_view is not None
    assert reference_view.property("visible") is True

    controller.mode = "Long cats"
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))

    assert reference_view.property("visible") is False
    assert long_cat_view.property("visible") is True
    long_cats = visualizer_delegates(long_cat_view, "longCatBar")
    assert len(long_cats) == 24
    strongest_long_cat = max(long_cats, key=lambda cat: cat.property("bandValue"))
    assert strongest_long_cat.property("bodyHeight") > strongest_long_cat.property(
        "minimumBodyHeight"
    )
    assert strongest_long_cat.property("headOffset") > 0.0
    assert strongest_long_cat.property("earAngle") > 0.0

    controller.mode = "Bouncing cats"
    application.processEvents()

    assert long_cat_view.property("visible") is False
    assert bouncing_cat_view.property("visible") is True
    bouncing_cats = visualizer_delegates(bouncing_cat_view, "bouncingCatHead")
    assert len(bouncing_cats) == 24
    strongest_bouncing_cat = max(bouncing_cats, key=lambda cat: cat.property("bandValue"))
    assert strongest_bouncing_cat.property("verticalOffset") > 0.0

    controller.toggleRunning()
    del engine


def test_visualizer_delegates_stay_inside_responsive_rows(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    for width, height in ((520, 480), (960, 720), (1440, 900)):
        root.setProperty("width", width)
        root.setProperty("height", height)
        application.processEvents()

        visualizers = (
            (root.findChild(QQuickItem, "referenceVisualizer"), "spectrumBar"),
            (root.findChild(QQuickItem, "longCatVisualizer"), "longCatBar"),
            (root.findChild(QQuickItem, "bouncingCatVisualizer"), "bouncingCatHead"),
        )
        for row, object_name in visualizers:
            assert row is not None
            delegates = visualizer_delegates(row, object_name)
            assert len(delegates) == 24
            row_width = row.property("width")
            for delegate in delegates:
                assert delegate.property("x") >= 0.0
                right_edge = delegate.property("x") + delegate.property("width")
                assert right_edge <= row_width + 0.5

        long_cat_row = root.findChild(QQuickItem, "longCatVisualizer")
        bouncing_cat_row = root.findChild(QQuickItem, "bouncingCatVisualizer")
        assert long_cat_row is not None
        assert bouncing_cat_row is not None

        for cat in visualizer_delegates(long_cat_row, "longCatBar"):
            assert cat.property("headTop") >= 0.0
            assert cat.property("bodyTop") >= 0.0

        for cat in visualizer_delegates(bouncing_cat_row, "bouncingCatHead"):
            assert cat.property("headTop") >= 0.0
            assert cat.property("headBottom") <= cat.property("height") + 0.5

    del engine
