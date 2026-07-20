from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlError  # noqa: E402

from white_cat_visualizer.app import create_engine  # noqa: E402
from white_cat_visualizer.presentation import VisualizerController  # noqa: E402


def main() -> int:
    application = QGuiApplication([])
    controller = VisualizerController()
    qml_warnings: list[QQmlError] = []
    engine = create_engine(controller, qml_warnings)
    if qml_warnings or not engine.rootObjects():
        for warning in qml_warnings:
            print(warning, file=sys.stderr)
        return 1

    QTimer.singleShot(0, application.quit)
    exit_code = application.exec()
    del engine
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
