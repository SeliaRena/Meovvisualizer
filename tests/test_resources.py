from __future__ import annotations

import importlib

import pytest

qt_core = pytest.importorskip("PySide6.QtCore")
resource_module = importlib.import_module("resource_rc")

QFile = qt_core.QFile
QIODevice = qt_core.QIODevice


def test_resource_module_is_importable() -> None:
    assert resource_module is not None


@pytest.mark.parametrize(
    "resource_path",
    [
        ":/qml/Main.qml",
        ":/qml/SettingsWindow.qml",
        ":/qml/components/VisualTokens.qml",
        ":/qml/long_bar_cat/long_bar_cat_icon.png",
    ],
)
def test_required_qml_and_icon_resources_resolve(resource_path: str) -> None:
    resource = QFile(resource_path)

    assert resource.exists()
    assert resource.open(QIODevice.OpenModeFlag.ReadOnly)
    assert resource.size() > 0
