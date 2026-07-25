from __future__ import annotations

import sys
import warnings
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, QQmlError

from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.source import AudioSource
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode
from white_cat_visualizer.audio.windows_loopback import (
    WindowsAudioError,
    create_windows_loopback_sources,
)
from white_cat_visualizer.presentation import VisualizerController
from white_cat_visualizer.settings import (
    ApplicationSettings,
    JsonSettingsStore,
    SettingsManager,
    default_settings_path,
)

import resource_rc # noqa: F401

QML_PATH = Path(__file__).parent / "ui" / "qml" / "Main.qml"
ICON_PATH = Path(__file__).parent / "ui" / "qml" / "long_bar_cat" / "long_bar_cat_icon.png"
APPLICATION_NAME = "Meovvisualizer"
APPLICATION_VERSION = "0.1.0"
ORGANIZATION_NAME = "Meovvisualizer"


def create_controller(settings: ApplicationSettings | None = None) -> VisualizerController:
    sources: list[AudioSource] = [SyntheticAudioSource(mode) for mode in SyntheticMode]
    if sys.platform == "win32":
        try:
            sources.extend(create_windows_loopback_sources())
        except WindowsAudioError as error:
            warnings.warn(str(error), RuntimeWarning, stacklevel=2)
    analyzer = SpectrumAnalyzer()
    default_source_id = f"synthetic:{SyntheticMode.BASS_PULSE.value}"
    initial_source_id = default_source_id
    initial_mode: str | None = None
    initial_sensitivity = 1.0
    if settings is not None:
        available_source_ids = {source.source_id for source in sources}
        if settings.source_id in available_source_ids:
            initial_source_id = settings.source_id
        elif settings.source_id is not None:
            warnings.warn(
                f"saved source {settings.source_id!r} is unavailable; using synthetic bass pulse",
                RuntimeWarning,
                stacklevel=2,
            )
        if settings.mode in VisualizerController.mode_names():
            initial_mode = settings.mode
        else:
            warnings.warn(
                f"saved visualizer mode {settings.mode!r} is unavailable; using reference bars",
                RuntimeWarning,
                stacklevel=2,
            )
        initial_sensitivity = settings.sensitivity
    return VisualizerController(
        sources,
        analyzer,
        initial_source_id=initial_source_id,
        initial_mode=initial_mode,
        initial_sensitivity=initial_sensitivity,
    )


def create_engine(
    controller: VisualizerController,
    qml_warnings: list[QQmlError] | None = None,
    settings_manager: SettingsManager | None = None,
) -> QQmlApplicationEngine:
    engine = QQmlApplicationEngine()
    if qml_warnings is not None:
        engine.warnings.connect(qml_warnings.extend)
    if settings_manager is None:
        settings_manager = SettingsManager(parent=engine)
    engine.setInitialProperties({"controller": controller, "settingsManager": settings_manager})
    engine.load(QUrl("qrc:/qml/Main.qml"))
    return engine


def main(arguments: Sequence[str] | None = None) -> int:
    application_arguments = list(arguments) if arguments is not None else list(sys.argv)
    smoke_test = "--smoke-test" in application_arguments
    application_arguments = [
        argument for argument in application_arguments if argument != "--smoke-test"
    ]
    application = QGuiApplication(application_arguments)
    application.setApplicationName(APPLICATION_NAME)
    application.setApplicationVersion(APPLICATION_VERSION)
    application.setOrganizationName(ORGANIZATION_NAME)
    application.setWindowIcon(QIcon(":/qml/long_bar_cat/long_bar_cat_icon.png"))

    settings_manager = SettingsManager(JsonSettingsStore(default_settings_path()))
    controller = create_controller(settings_manager.settings)
    settings_manager.watch_controller(controller)
    application.aboutToQuit.connect(controller.shutdown)
    engine = create_engine(controller, settings_manager=settings_manager)
    if not engine.rootObjects():
        controller.shutdown()
        return 1
    if smoke_test:
        QTimer.singleShot(0, application.quit)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
