from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import cast

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtCore import QObject, QTimer  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlError  # noqa: E402

from white_cat_visualizer.app import create_controller, create_engine  # noqa: E402


def main() -> int:
    application = QGuiApplication([])
    controller = create_controller()
    qml_warnings: list[QQmlError] = []
    engine = create_engine(controller, qml_warnings)
    if qml_warnings or not engine.rootObjects():
        for warning in qml_warnings:
            print(warning, file=sys.stderr)
        return 1

    root = engine.rootObjects()[0]
    bars = root.findChild(QObject, "spectrumBars")
    if bars is None or bars.property("count") != 24:
        count = 0 if bars is None else bars.property("count")
        print(f"expected 24 spectrum bars, found {count}", file=sys.stderr)
        return 1

    controller.toggleRunning()
    application.processEvents()
    band_values = controller.property("bands")
    rms_value = controller.property("rms")
    peak_value = controller.property("peak")
    typed_bands = cast(list[object], band_values) if isinstance(band_values, list) else []
    if (
        not typed_bands
        or not any(isinstance(value, (int, float)) and value > 0.0 for value in typed_bands)
        or not isinstance(rms_value, float)
        or rms_value <= 0.0
        or not isinstance(peak_value, float)
        or peak_value <= 0.0
    ):
        print("synthetic pipeline did not publish visible values", file=sys.stderr)
        return 1
    controller.toggleRunning()

    QTimer.singleShot(0, application.quit)
    exit_code = application.exec()
    del engine
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
