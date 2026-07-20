from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlError

from white_cat_visualizer.presentation import VisualizerController

QML_PATH = Path(__file__).parent / "ui" / "qml" / "Main.qml"


def create_engine(
    controller: VisualizerController, qml_warnings: list[QQmlError] | None = None
) -> QQmlApplicationEngine:
    engine = QQmlApplicationEngine()
    if qml_warnings is not None:
        engine.warnings.connect(qml_warnings.extend)
    engine.setInitialProperties({"controller": controller})
    engine.load(QUrl.fromLocalFile(str(QML_PATH)))
    return engine


def main(arguments: Sequence[str] | None = None) -> int:
    application = QGuiApplication(list(arguments) if arguments is not None else sys.argv)
    controller = VisualizerController()
    engine = create_engine(controller)
    if not engine.rootObjects():
        return 1
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
