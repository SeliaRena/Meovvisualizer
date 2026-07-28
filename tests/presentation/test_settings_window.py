from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

qt_core = pytest.importorskip("PySide6.QtCore")
qt_gui = pytest.importorskip("PySide6.QtGui")
application_module = pytest.importorskip("white_cat_visualizer.app")

QObject = qt_core.QObject
QMetaObject = qt_core.QMetaObject
Qt = qt_core.Qt
QGuiApplication = qt_gui.QGuiApplication
create_controller = application_module.create_controller
create_engine = application_module.create_engine


@pytest.fixture(scope="module")
def application() -> QGuiApplication:
    existing = QGuiApplication.instance()
    return existing if isinstance(existing, QGuiApplication) else QGuiApplication([])


def test_settings_window_is_single_instance_and_tracks_always_on_top(
    application: QGuiApplication,
) -> None:
    controller = create_controller()
    qml_warnings: list[object] = []
    engine = create_engine(controller, qml_warnings)
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
    assert int(settings_window.property("flags")) & always_on_top_flag == 0
    assert root.property("windowAlwaysOnTop") is True
    assert always_on_top_switch.property("checked") is True

    root.setProperty("x", 120)
    root.setProperty("y", 80)
    root.setProperty("width", 960)
    root.setProperty("height", 720)
    application.processEvents()
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
