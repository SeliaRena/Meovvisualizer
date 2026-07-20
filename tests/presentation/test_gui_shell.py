from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

qt_core = pytest.importorskip("PySide6.QtCore")
qt_gui = pytest.importorskip("PySide6.QtGui")
application_module = pytest.importorskip("white_cat_visualizer.app")
presentation = pytest.importorskip("white_cat_visualizer.presentation")

QObject = qt_core.QObject
QColor = qt_gui.QColor
QGuiApplication = qt_gui.QGuiApplication
create_engine = application_module.create_engine
VisualizerController = presentation.VisualizerController


@pytest.fixture(scope="module")
def application() -> QGuiApplication:
    existing = QGuiApplication.instance()
    return existing if isinstance(existing, QGuiApplication) else QGuiApplication([])


def test_shell_loads_and_keeps_canvas_usable_at_supported_sizes(
    application: QGuiApplication,
) -> None:
    controller = VisualizerController()
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
    controller = VisualizerController()
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
