from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from threading import Event

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from white_cat_visualizer.audio.source import AudioSource
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode

qt_core = pytest.importorskip("PySide6.QtCore")
qt_gui = pytest.importorskip("PySide6.QtGui")
qt_test = pytest.importorskip("PySide6.QtTest")
application_module = pytest.importorskip("white_cat_visualizer.app")

QObject = qt_core.QObject
QEventLoop = qt_core.QEventLoop
QMetaObject = qt_core.QMetaObject
QTimer = qt_core.QTimer
Qt = qt_core.Qt
QGuiApplication = qt_gui.QGuiApplication
QTest = qt_test.QTest
create_controller = application_module.create_controller
create_engine = application_module.create_engine
JsonSettingsStore = application_module.JsonSettingsStore
SettingsManager = application_module.SettingsManager


@pytest.fixture(scope="module")
def application() -> QGuiApplication:
    existing = QGuiApplication.instance()
    return existing if isinstance(existing, QGuiApplication) else QGuiApplication([])


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

    assert not timed_out, "QML state did not update"
    assert predicate()


def test_settings_window_is_single_instance_and_tracks_always_on_top(
    application: QGuiApplication,
    tmp_path: Path,
) -> None:
    controller = create_controller()
    store = JsonSettingsStore(tmp_path / "settings.json")
    settings_manager = SettingsManager(store)
    qml_warnings: list[object] = []
    engine = create_engine(controller, qml_warnings, settings_manager)
    assert qml_warnings == []

    root = engine.rootObjects()[0]
    settings_button = root.findChild(QObject, "settingsButton")
    minimize_button = root.findChild(QObject, "minimizeButton")
    settings_window = root.findChild(QObject, "settingsWindow")
    settings_close_button = root.findChild(QObject, "settingsCloseButton")
    always_on_top_switch = root.findChild(QObject, "alwaysOnTopSwitch")

    assert settings_button is not None
    assert minimize_button is not None
    assert settings_window is not None
    assert settings_close_button is not None
    assert always_on_top_switch is not None
    assert settings_button.property("activeFocusOnTab") is False
    assert settings_button.property("x") < minimize_button.property("x")
    assert settings_window.property("visible") is False
    assert settings_window.property("transientParent") == root

    always_on_top_flag = int(Qt.WindowType.WindowStaysOnTopHint)
    assert root.property("windowAlwaysOnTop") is True
    assert always_on_top_switch.property("checked") is True

    original_geometry = (
        root.property("x"),
        root.property("y"),
        root.property("width"),
        root.property("height"),
    )

    root.setProperty("windowAlwaysOnTop", False)
    application.processEvents()

    assert root.property("visible") is True
    assert int(root.property("flags")) & always_on_top_flag == 0
    assert always_on_top_switch.property("checked") is False
    assert store.load().window_always_on_top is False
    assert (
        root.property("x"),
        root.property("y"),
        root.property("width"),
        root.property("height"),
    ) == original_geometry

    assert QMetaObject.invokeMethod(always_on_top_switch, "click")
    application.processEvents()

    assert root.property("windowAlwaysOnTop") is True
    assert int(root.property("flags")) & always_on_top_flag
    assert store.load().window_always_on_top is True

    assert QMetaObject.invokeMethod(root, "openSettingsWindow")
    application.processEvents()
    assert settings_window.property("visible") is True

    settings_window.close()
    application.processEvents()
    assert settings_window.property("visible") is False

    assert QMetaObject.invokeMethod(root, "openSettingsWindow")
    application.processEvents()
    assert root.findChild(QObject, "settingsWindow") == settings_window
    assert settings_window.property("visible") is True

    settings_window.close()
    controller.shutdown()
    del engine


def test_animation_speed_slider_uses_main_window_as_single_source(
    application: QGuiApplication,
    tmp_path: Path,
) -> None:
    controller = create_controller()
    store = JsonSettingsStore(tmp_path / "settings.json")
    settings_manager = SettingsManager(store)
    qml_warnings: list[object] = []
    engine = create_engine(controller, qml_warnings, settings_manager)

    assert qml_warnings == []
    root = engine.rootObjects()[0]
    settings_window = root.findChild(QObject, "settingsWindow")
    slider = root.findChild(QObject, "marqueeSpeedSlider")
    speed_value = root.findChild(QObject, "marqueeSpeedValue")
    marquee = root.findChild(QObject, "vibingMarquee")

    assert settings_window is not None
    assert slider is not None
    assert speed_value is not None
    assert marquee is not None
    assert root.property("marqueePixelsPerSecond") == pytest.approx(150)
    assert slider.property("from") == pytest.approx(50)
    assert slider.property("to") == pytest.approx(1000)
    assert slider.property("stepSize") == pytest.approx(50)
    assert slider.property("snapsAlways") is True
    assert slider.property("live") is True
    assert slider.property("value") == pytest.approx(150)
    assert marquee.property("pixelsPerSecond") == pytest.approx(150)
    assert speed_value.property("text") == "150 px/s"

    assert QMetaObject.invokeMethod(root, "openSettingsWindow")
    slider.forceActiveFocus()
    QTest.keyClick(settings_window, Qt.Key.Key_Right)
    application.processEvents()

    assert root.property("marqueePixelsPerSecond") == pytest.approx(200)
    assert slider.property("value") == pytest.approx(200)
    assert store.load().marquee_pixels_per_second == 200

    slider.setProperty("value", 450)
    assert QMetaObject.invokeMethod(slider, "moved")
    application.processEvents()

    assert root.property("marqueePixelsPerSecond") == pytest.approx(450)
    assert marquee.property("pixelsPerSecond") == pytest.approx(450)
    assert speed_value.property("text") == "450 px/s"
    assert store.load().marquee_pixels_per_second == 450

    root.setProperty("marqueePixelsPerSecond", 1000)
    application.processEvents()

    assert slider.property("value") == pytest.approx(1000)
    assert marquee.property("pixelsPerSecond") == pytest.approx(1000)
    assert speed_value.property("text") == "1000 px/s"

    settings_window.close()
    controller.shutdown()
    del engine


def test_audio_rescan_control_disables_while_scanning_and_shows_status(
    application: QGuiApplication,
) -> None:
    entered = Event()
    release = Event()
    call_count = 0

    def provider() -> tuple[AudioSource, ...]:
        nonlocal call_count
        call_count += 1
        sources: tuple[AudioSource, ...] = tuple(
            SyntheticAudioSource(mode) for mode in SyntheticMode
        )
        if call_count > 1:
            entered.set()
            assert release.wait(timeout=1.0)
        return sources

    controller = create_controller(audio_source_provider=provider)
    qml_warnings: list[object] = []
    engine = create_engine(controller, qml_warnings)
    assert qml_warnings == []
    root = engine.rootObjects()[0]
    category = root.findChild(QObject, "audioSettingsCategory")
    setting = root.findChild(QObject, "audioDeviceSetting")
    button = root.findChild(QObject, "rescanAudioDevicesButton")
    status = root.findChild(QObject, "audioSourceRefreshStatus")

    assert category is not None
    assert setting is not None
    assert button is not None
    assert status is not None
    assert category.property("text") == "AUDIO"
    assert button.property("text") == "Rescan devices"
    assert button.property("enabled") is True
    assert status.property("visible") is False

    assert QMetaObject.invokeMethod(button, "click")
    assert entered.wait(timeout=1.0)
    try:
        application.processEvents()
        assert controller.refreshingAudioSources is True
        assert button.property("enabled") is False
        assert button.property("text") == "Scanning…"
        assert status.property("visible") is True
        assert status.property("text") == "Scanning audio output devices…"
    finally:
        release.set()

    wait_until(lambda: not controller.refreshingAudioSources)
    application.processEvents()

    assert button.property("enabled") is True
    assert button.property("text") == "Rescan devices"
    assert status.property("visible") is True
    assert status.property("text") == "No changes detected"
    assert qml_warnings == []

    controller.shutdown()
    del engine


def test_refreshed_catalog_updates_existing_source_selector_model(
    application: QGuiApplication,
) -> None:
    bass = SyntheticAudioSource(SyntheticMode.BASS_PULSE)
    replacement_bass = SyntheticAudioSource(SyntheticMode.BASS_PULSE)
    sine = SyntheticAudioSource(SyntheticMode.SINE)
    snapshots: list[tuple[AudioSource, ...]] = [
        (bass,),
        (replacement_bass, sine),
    ]

    def provider() -> tuple[AudioSource, ...]:
        return snapshots.pop(0)

    controller = create_controller(audio_source_provider=provider)
    qml_warnings: list[object] = []
    engine = create_engine(controller, qml_warnings)
    assert qml_warnings == []
    root = engine.rootObjects()[0]
    source_control = root.findChild(QObject, "sourceControl")

    assert source_control is not None
    assert source_control.property("count") == 1
    assert source_control.property("currentText") == bass.display_name

    controller.refreshAudioSources()
    wait_until(lambda: not controller.refreshingAudioSources)
    application.processEvents()

    assert source_control.property("count") == 2
    assert source_control.property("currentText") == replacement_bass.display_name
    assert controller.sourceId == bass.source_id
    assert qml_warnings == []

    controller.shutdown()
    del engine
