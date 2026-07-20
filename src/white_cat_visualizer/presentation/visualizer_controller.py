from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot


class VisualizerController(QObject):
    """Python-owned state exposed to the Phase 1 QML shell."""

    sourceChanged = Signal()
    modeChanged = Signal()
    sensitivityChanged = Signal()
    runningChanged = Signal()

    _SOURCE_NAMES = ("System output (placeholder)",)
    _MODE_NAMES = ("Long cat bars", "Bouncing cat heads")
    _BAND_COUNT = 24

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._source = self._SOURCE_NAMES[0]
        self._mode = self._MODE_NAMES[0]
        self._sensitivity = 1.0
        self._running = False
        self._bands = [0.0] * self._BAND_COUNT

    def _get_source_names(self) -> list[str]:
        return list(self._SOURCE_NAMES)

    sourceNames = Property(list, _get_source_names, constant=True)

    def _get_source(self) -> str:
        return self._source

    def _set_source(self, value: str) -> None:
        if value not in self._SOURCE_NAMES or value == self._source:
            return
        self._source = value
        self.sourceChanged.emit()

    source = Property(str, _get_source, _set_source, notify=sourceChanged)

    def _get_mode_names(self) -> list[str]:
        return list(self._MODE_NAMES)

    modeNames = Property(list, _get_mode_names, constant=True)

    def _get_mode(self) -> str:
        return self._mode

    def _set_mode(self, value: str) -> None:
        if value not in self._MODE_NAMES or value == self._mode:
            return
        self._mode = value
        self.modeChanged.emit()

    mode = Property(str, _get_mode, _set_mode, notify=modeChanged)

    def _get_sensitivity(self) -> float:
        return self._sensitivity

    def _set_sensitivity(self, value: float) -> None:
        clamped_value = min(max(value, 0.5), 2.0)
        if clamped_value == self._sensitivity:
            return
        self._sensitivity = clamped_value
        self.sensitivityChanged.emit()

    sensitivity = Property(float, _get_sensitivity, _set_sensitivity, notify=sensitivityChanged)

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @Property(float, constant=True)
    def rms(self) -> float:
        return 0.0

    @Property(float, constant=True)
    def peak(self) -> float:
        return 0.0

    def _get_bands(self) -> list[float]:
        return list(self._bands)

    bands = Property(list, _get_bands, constant=True)

    @Property(str, constant=True)
    def error(self) -> str:
        return ""

    @Slot()
    def toggleRunning(self) -> None:
        self._running = not self._running
        self.runningChanged.emit()
