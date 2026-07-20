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

from PySide6.QtCore import QEventLoop, QObject, QTimer  # noqa: E402
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
    repeaters = (
        ("spectrumBars", "reference bars"),
        ("longCatBars", "long cats"),
        ("bouncingCatHeads", "bouncing cat heads"),
    )
    for object_name, label in repeaters:
        repeater = root.findChild(QObject, object_name)
        if repeater is None or repeater.property("count") != 24:
            count = 0 if repeater is None else repeater.property("count")
            print(f"expected 24 {label}, found {count}", file=sys.stderr)
            return 1

    for mode in ("Reference bars", "Long cats", "Bouncing cats"):
        controller.setProperty("mode", mode)
        application.processEvents()
        if qml_warnings:
            for warning in qml_warnings:
                print(warning, file=sys.stderr)
            return 1

    controller.toggleRunning()
    update_loop = QEventLoop()
    poll_timer = QTimer()
    poll_timer.setInterval(0)
    poll_timer.timeout.connect(
        lambda: update_loop.quit() if any(controller.property("bands")) else None
    )
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.timeout.connect(update_loop.quit)
    poll_timer.start()
    timeout_timer.start(1_000)
    update_loop.exec()
    poll_timer.stop()
    timed_out = not timeout_timer.isActive()
    timeout_timer.stop()
    if timed_out:
        print("analysis worker did not publish before timeout", file=sys.stderr)
        controller.shutdown()
        return 1
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
        controller.shutdown()
        return 1
    controller.toggleRunning()

    QTimer.singleShot(0, application.quit)
    exit_code = application.exec()
    del engine
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
