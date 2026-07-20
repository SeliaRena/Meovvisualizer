from __future__ import annotations

import sys
import warnings
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlError

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.source import AudioSource
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode
from white_cat_visualizer.audio.windows_loopback import (
    WindowsAudioError,
    create_windows_loopback_sources,
)
from white_cat_visualizer.presentation import VisualizerController

QML_PATH = Path(__file__).parent / "ui" / "qml" / "Main.qml"


def create_controller() -> VisualizerController:
    sources: list[AudioSource] = [SyntheticAudioSource(mode) for mode in SyntheticMode]
    if sys.platform == "win32":
        try:
            sources.extend(create_windows_loopback_sources())
        except WindowsAudioError as error:
            warnings.warn(str(error), RuntimeWarning, stacklevel=2)
    analyzer = SpectrumAnalyzer()
    return VisualizerController(
        sources,
        analyzer,
        initial_source_id=f"synthetic:{SyntheticMode.BASS_PULSE.value}",
    )


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
    controller = create_controller()
    application.aboutToQuit.connect(controller.shutdown)
    engine = create_engine(controller)
    if not engine.rootObjects():
        controller.shutdown()
        return 1
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
