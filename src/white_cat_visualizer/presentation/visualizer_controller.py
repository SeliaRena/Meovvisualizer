from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import (
    Property,
    QCoreApplication,
    QObject,
    Qt,
    QTimer,
    Signal,
    Slot,
)

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.source import AudioSource


class VisualizerController(QObject):
    """Drive the temporary synthetic pipeline and expose render-ready UI state."""

    sourceChanged = Signal()
    modeChanged = Signal()
    sensitivityChanged = Signal()
    runningChanged = Signal()
    bandsChanged = Signal()
    rmsChanged = Signal()
    peakChanged = Signal()

    _MODE_NAMES = ("Reference bars", "Long cats", "Bouncing cats")
    _BAND_COUNT = 24
    _FRAME_INTERVAL_MS = 43

    def __init__(
        self,
        sources: Sequence[AudioSource],
        analyzer: SpectrumAnalyzer,
        *,
        initial_source_id: str | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        if not sources:
            raise ValueError("at least one audio source is required")
        if analyzer.band_count != self._BAND_COUNT:
            raise ValueError(f"analyzer must provide {self._BAND_COUNT} bands")

        source_by_name = {source.display_name: source for source in sources}
        if len(source_by_name) != len(sources):
            raise ValueError("audio source display names must be unique")
        source_by_id = {source.source_id: source for source in sources}
        if len(source_by_id) != len(sources):
            raise ValueError("audio source IDs must be unique")

        if initial_source_id is None:
            selected_source = sources[0]
        else:
            try:
                selected_source = source_by_id[initial_source_id]
            except KeyError as error:
                raise ValueError(f"unknown initial source ID: {initial_source_id}") from error

        self._sources = tuple(sources)
        self._source_by_name = source_by_name
        self._selected_source = selected_source
        self._analyzer = analyzer
        self._mode = self._MODE_NAMES[0]
        self._sensitivity = 1.0
        self._running = False
        self._bands = [0.0] * self._BAND_COUNT
        self._rms = 0.0
        self._peak = 0.0
        self._latest_frame: VisualizerFrame | None = None

        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.setInterval(self._FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self.processNextFrame)

    def _get_source_names(self) -> list[str]:
        return [source.display_name for source in self._sources]

    sourceNames = Property(list, _get_source_names, constant=True)

    def _get_source(self) -> str:
        return self._selected_source.display_name

    def _set_source(self, value: str) -> None:
        selected_source = self._source_by_name.get(value)
        if selected_source is None or selected_source is self._selected_source:
            return
        self._selected_source = selected_source
        self._reset_pipeline()
        self.sourceChanged.emit()
        if self._running:
            self.processNextFrame()

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
        self._publish_latest_frame()

    sensitivity = Property(float, _get_sensitivity, _set_sensitivity, notify=sensitivityChanged)

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @Property(float, notify=rmsChanged)
    def rms(self) -> float:
        return self._rms

    @Property(float, notify=peakChanged)
    def peak(self) -> float:
        return self._peak

    def _get_bands(self) -> list[float]:
        return list(self._bands)

    bands = Property(list, _get_bands, notify=bandsChanged)

    @Property(str, constant=True)
    def error(self) -> str:
        return ""

    @Slot()
    def toggleRunning(self) -> None:
        if self._running:
            self._timer.stop()
            self._running = False
            self._reset_pipeline()
        else:
            self._reset_pipeline()
            self._running = True
            self.processNextFrame()
            if QCoreApplication.instance() is not None:
                self._timer.start()
        self.runningChanged.emit()

    @Slot()
    def processNextFrame(self) -> None:
        if not self._running:
            return
        audio_frame = self._selected_source.next_frame()
        self._latest_frame = self._analyzer.analyze(audio_frame)
        self._publish_latest_frame()

    def _reset_pipeline(self) -> None:
        self._selected_source.reset()
        self._analyzer.reset()
        self._latest_frame = None
        self._set_output([0.0] * self._BAND_COUNT, 0.0, 0.0)

    def _publish_latest_frame(self) -> None:
        if self._latest_frame is None:
            return
        scaled_bands = [min(value * self._sensitivity, 1.0) for value in self._latest_frame.bands]
        scaled_rms = min(self._latest_frame.rms * self._sensitivity, 1.0)
        scaled_peak = min(self._latest_frame.peak * self._sensitivity, 1.0)
        self._set_output(scaled_bands, scaled_rms, scaled_peak)

    def _set_output(self, bands: list[float], rms: float, peak: float) -> None:
        if bands != self._bands:
            self._bands = bands
            self.bandsChanged.emit()
        if rms != self._rms:
            self._rms = rms
            self.rmsChanged.emit()
        if peak != self._peak:
            self._peak = peak
            self.peakChanged.emit()
