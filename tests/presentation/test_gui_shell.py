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
QPointF = qt_core.QPointF
QQuickItem = qt_quick.QQuickItem
QEventLoop = qt_core.QEventLoop
QMetaObject = qt_core.QMetaObject
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
    qml_warnings: list[object] = []
    engine = create_engine(controller, qml_warnings)
    roots = engine.rootObjects()
    assert qml_warnings == []
    assert len(roots) == 1
    root = roots[0]
    controls_panel = root.findChild(QQuickItem, "expandableControlsPanel")
    controls = root.findChild(QQuickItem, "controlSurface")
    canvas = root.findChild(QQuickItem, "visualizerCanvas")

    assert controls_panel is not None
    assert controls is not None
    assert canvas is not None
    minimum_width = root.property("minimumWidth")
    minimum_height = root.property("minimumHeight")
    assert minimum_width > 0
    assert minimum_height > 0

    for width, height in (
        (minimum_width, minimum_height),
        (max(960, minimum_width), max(720, minimum_height)),
        (max(1440, minimum_width), max(900, minimum_height)),
    ):
        root.setProperty("width", width)
        root.setProperty("height", height)
        application.processEvents()

        controls_bottom = controls_panel.mapToScene(QPointF()).y() + controls_panel.property(
            "height"
        )
        canvas_top = canvas.mapToScene(QPointF()).y()
        assert controls.property("width") > 0
        assert controls.property("height") > 0
        assert canvas.property("width") > 0
        assert canvas.property("height") >= root.property("minimumCanvasHeight")
        assert controls_bottom <= canvas_top + 0.5

    del engine


def test_shell_uses_centralized_tint_glass_tokens(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    theme = root.findChild(QObject, "themeTokens")
    main_surface = root.findChild(QObject, "mainGlassSurface")
    controls = root.findChild(QObject, "controlSurface")
    canvas = root.findChild(QObject, "visualizerCanvas")

    assert theme is not None
    assert main_surface is not None
    assert controls is not None
    assert canvas is not None
    assert root.property("color") == QColor("transparent")
    assert main_surface.property("color") == QColor("#C20B0912")
    assert canvas.property("color") == QColor("#24171327")
    assert theme.property("primaryText") == QColor("#F7F7FA")
    assert theme.property("standardBorder") == QColor("#32FFFFFF")
    assert theme.property("accent") == QColor("#A491FF")
    assert theme.property("transitionDuration") == 140

    outer_inset = theme.property("outerInset")
    assert main_surface.property("x") == pytest.approx(outer_inset)
    assert main_surface.property("y") == pytest.approx(outer_inset)
    assert controls.property("width") > 0
    assert canvas.property("width") > 0

    del engine


def test_glass_frame_and_narrow_contract_track_supported_window_sizes(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    main_surface = root.findChild(QObject, "mainGlassSurface")

    assert main_surface is not None
    expected_fill = QColor("#C20B0912")
    minimum_width = root.property("minimumWidth")
    minimum_height = root.property("minimumHeight")
    breakpoint = root.property("wideToolbarMinimumWidth")
    supported_widths = (
        minimum_width,
        max(minimum_width, breakpoint - 1),
        max(minimum_width, breakpoint),
        max(minimum_width, breakpoint + 240),
    )

    for width in supported_widths:
        height = max(minimum_height, 720)
        root.setProperty("width", width)
        root.setProperty("height", height)
        application.processEvents()

        effective_inset = root.property("effectiveOuterInset")
        assert root.findChild(QObject, "mainGlassSurface") == main_surface
        assert root.property("width") == pytest.approx(width)
        assert root.property("height") == pytest.approx(height)
        assert root.property("narrow") is (width < breakpoint)
        assert root.property("opacity") == pytest.approx(1.0)
        assert main_surface.property("x") == pytest.approx(effective_inset)
        assert main_surface.property("y") == pytest.approx(effective_inset)
        assert main_surface.property("width") == pytest.approx(width - 2 * effective_inset)
        assert main_surface.property("height") == pytest.approx(height - 2 * effective_inset)
        assert main_surface.property("visible") is True
        assert main_surface.property("clip") is False
        assert main_surface.property("opacity") == pytest.approx(1.0)
        assert main_surface.property("color") == expected_fill

    del engine


def test_controls_and_visualizer_remain_usable_across_layout_modes(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    controls_panel = root.findChild(QQuickItem, "expandableControlsPanel")
    controls = root.findChild(QQuickItem, "controlSurface")
    controls_flow = root.findChild(QQuickItem, "controlsFlow")
    running_control = root.findChild(QQuickItem, "runningControl")
    canvas = root.findChild(QQuickItem, "visualizerCanvas")

    assert controls_panel is not None
    assert controls is not None
    assert controls_flow is not None
    assert running_control is not None
    assert canvas is not None

    minimum_width = root.property("minimumWidth")
    minimum_height = root.property("minimumHeight")
    breakpoint = root.property("wideToolbarMinimumWidth")
    for width in (
        minimum_width,
        max(minimum_width, breakpoint - 1),
        max(minimum_width, breakpoint),
        max(minimum_width, breakpoint + 64),
    ):
        root.setProperty("width", width)
        root.setProperty("height", max(minimum_height, 720))
        application.processEvents()

        controls_top = controls.mapToScene(QPointF()).y()
        panel_bottom = controls_panel.mapToScene(QPointF()).y() + controls_panel.property("height")
        controls_bottom = controls_top + controls.property("height")
        button_top = running_control.mapToScene(QPointF()).y()
        button_bottom = button_top + running_control.property("height")
        canvas_top = canvas.mapToScene(QPointF()).y()

        assert controls.property("height") >= controls_flow.property("implicitHeight")
        assert button_top >= controls_top
        assert button_bottom <= controls_bottom + 0.5
        assert running_control.property("width") > 0
        assert running_control.property("height") > 0
        assert running_control.property("enabled") is True
        assert canvas.property("width") > 0
        assert canvas.property("height") > 0
        assert canvas_top >= panel_bottom - 0.5
        assert root.property("narrow") is (width < breakpoint)

    del engine


def test_controls_panel_expands_and_collapses_without_losing_usable_content(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    panel = root.findChild(QQuickItem, "expandableControlsPanel")
    toggle = root.findChild(QQuickItem, "controlsToggleButton")
    marquee = root.findChild(QQuickItem, "vibingMarquee")
    canvas = root.findChild(QQuickItem, "visualizerCanvas")

    assert panel is not None
    assert toggle is not None
    assert marquee is not None
    assert canvas is not None
    assert panel.property("expanded") is True
    expanded_height = panel.property("height")

    assert QMetaObject.invokeMethod(toggle, "click")
    wait_until(
        lambda: panel.property("expanded") is False and panel.property("height") < expanded_height
    )
    collapsed_height = panel.property("height")

    assert collapsed_height > 0
    assert marquee.property("active") is True
    assert toggle.property("activeFocus") is True
    assert canvas.property("width") > 0
    assert canvas.property("height") > 0

    assert QMetaObject.invokeMethod(toggle, "click")
    wait_until(
        lambda: panel.property("expanded") is True and panel.property("height") > collapsed_height
    )

    assert marquee.property("active") is False
    del engine


def test_marquee_speed_is_distance_based_and_changes_without_restart(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    toggle = root.findChild(QQuickItem, "controlsToggleButton")
    marquee = root.findChild(QQuickItem, "vibingMarquee")
    travel_animation = root.findChild(QObject, "marqueeTravelAnimation")

    assert toggle is not None
    assert marquee is not None
    assert travel_animation is not None
    assert root.property("marqueePixelsPerSecond") == pytest.approx(200)
    assert marquee.property("pixelsPerSecond") == pytest.approx(200)
    assert marquee.property("active") is False
    assert travel_animation.property("running") is False

    measurements: list[tuple[float, int]] = []
    for width in (root.property("minimumWidth"), 1200):
        root.setProperty("width", width)
        application.processEvents()

        travel_distance = marquee.property("travelDistance")
        travel_duration = marquee.property("travelDuration")
        expected_duration = max(
            1,
            round(travel_distance / marquee.property("effectivePixelsPerSecond") * 1000),
        )
        actual_speed = travel_distance / travel_duration * 1000

        assert travel_duration == expected_duration
        assert actual_speed == pytest.approx(200, abs=0.1)
        measurements.append((travel_distance, travel_duration))

    assert measurements[1][0] > measurements[0][0]
    assert measurements[1][1] > measurements[0][1]

    assert QMetaObject.invokeMethod(toggle, "click")
    wait_until(lambda: marquee.property("active") is True)
    assert travel_animation.property("running") is True

    marquee.setProperty("travelProgress", 0.5)
    root.setProperty("marqueePixelsPerSecond", 1000)

    assert marquee.property("pixelsPerSecond") == pytest.approx(1000)
    assert marquee.property("travelProgress") == pytest.approx(0.5)

    assert QMetaObject.invokeMethod(toggle, "click")
    wait_until(lambda: marquee.property("active") is False)
    assert travel_animation.property("running") is False
    assert marquee.property("travelProgress") == pytest.approx(0.0)

    del engine


def test_running_button_controls_start_and_stop_state(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    running_control = root.findChild(QQuickItem, "runningControl")

    assert running_control is not None
    assert running_control.property("enabled") is True
    assert running_control.property("text") == "Start"
    assert controller.running is False

    assert QMetaObject.invokeMethod(running_control, "click")
    wait_until(lambda: controller.running and any(controller.bands))

    assert running_control.property("text") == "Stop"

    assert QMetaObject.invokeMethod(running_control, "click")
    wait_until(lambda: not controller.running)

    assert running_control.property("text") == "Start"
    assert controller.bands == [0.0] * 24
    assert controller.rms == 0.0
    assert controller.peak == 0.0
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


def test_primary_controls_have_readable_disabled_states(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    source_control = root.findChild(QObject, "sourceControl")
    source_background = root.findChild(QObject, "sourceControlBackground")
    source_text = root.findChild(QObject, "sourceControlText")
    running_control = root.findChild(QObject, "runningControl")
    running_background = root.findChild(QObject, "runningControlBackground")
    running_text = root.findChild(QObject, "runningControlText")

    assert source_control is not None
    assert source_background is not None
    assert source_text is not None
    assert running_control is not None
    assert running_background is not None
    assert running_text is not None

    source_control.setProperty("enabled", False)
    running_control.setProperty("enabled", False)
    wait_until(
        lambda: (
            source_background.property("color") == QColor("#1AFFFFFF")
            and running_background.property("color") == QColor("#1AFFFFFF")
        )
    )

    assert source_text.property("color") == QColor("#5F5B68")
    assert running_text.property("color") == QColor("#5F5B68")

    del engine


def test_shell_renders_current_visualizers_and_separate_levels(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    bars = root.findChild(QObject, "spectrumBars")
    long_cats = root.findChild(QObject, "longCatBars")
    rms_level = root.findChild(QObject, "rmsLevel")
    peak_level = root.findChild(QObject, "peakLevel")

    assert bars is not None
    assert bars.property("count") == 24
    assert long_cats is not None
    assert long_cats.property("count") == 24
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


def test_mode_switching_and_long_cat_mapping_are_deterministic(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    reference_view = root.findChild(QQuickItem, "referenceVisualizer")
    long_cat_view = root.findChild(QQuickItem, "longCatVisualizer")

    assert reference_view is not None
    assert long_cat_view is not None
    assert reference_view.property("visible") is True

    controller.mode = "Long cats"
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))

    assert reference_view.property("visible") is False
    assert long_cat_view.property("visible") is True
    long_cats = visualizer_delegates(long_cat_view, "longCatBar")
    assert len(long_cats) == 24
    strongest_long_cat = max(long_cats, key=lambda cat: cat.property("bandValue"))
    weakest_long_cat = min(long_cats, key=lambda cat: cat.property("bandValue"))
    assert strongest_long_cat.property("bodyHeight") > weakest_long_cat.property("bodyHeight")
    assert strongest_long_cat.property("headTop") >= 0.0
    assert strongest_long_cat.property("earAngle") > 0.0

    controller.toggleRunning()
    del engine


def test_visualizer_delegates_stay_inside_responsive_rows(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    engine = create_engine(controller)
    root = engine.rootObjects()[0]

    minimum_width = root.property("minimumWidth")
    minimum_height = root.property("minimumHeight")
    for width, height in (
        (minimum_width, minimum_height),
        (max(960, minimum_width), max(720, minimum_height)),
        (max(1440, minimum_width), max(900, minimum_height)),
    ):
        root.setProperty("width", width)
        root.setProperty("height", height)
        application.processEvents()

        visualizers = (
            (root.findChild(QQuickItem, "referenceVisualizer"), "spectrumBar"),
            (root.findChild(QQuickItem, "longCatVisualizer"), "longCatBar"),
        )
        for row, object_name in visualizers:
            assert row is not None
            delegates = visualizer_delegates(row, object_name)
            assert len(delegates) == 24
            row_width = row.property("width")
            row_height = row.property("height")
            for delegate in delegates:
                position = delegate.mapToItem(row, QPointF())
                assert position.x() >= -0.5
                assert position.y() >= -0.5
                right_edge = position.x() + delegate.property("width")
                bottom_edge = position.y() + delegate.property("height")
                assert right_edge <= row_width + 0.5
                assert bottom_edge <= row_height + 0.5

        long_cat_row = root.findChild(QQuickItem, "longCatVisualizer")
        assert long_cat_row is not None

        for cat in visualizer_delegates(long_cat_row, "longCatBar"):
            assert cat.property("headTop") >= 0.0
            assert cat.property("bodyTop") >= 0.0

    del engine
