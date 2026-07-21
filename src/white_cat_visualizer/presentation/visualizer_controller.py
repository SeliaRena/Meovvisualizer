from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.source import AudioSource
from white_cat_visualizer.runtime.analysis_worker import (
    AnalysisWorker,
    WorkerFailure,
    WorkerFailureStage,
)


class ControllerErrorCode(StrEnum):
    ANALYSIS_WORKER_FAILED = "analysis-worker-failed"
    AUDIO_SOURCE_FAILED = "audio-source-failed"


@dataclass(frozen=True, slots=True)
class ControllerErrorState:
    code: ControllerErrorCode
    message: str


class VisualizerController(QObject):
    """Own runtime lifecycle and expose render-ready state on the UI thread."""

    sourceChanged = Signal()
    modeChanged = Signal()
    sensitivityChanged = Signal()
    runningChanged = Signal()
    errorChanged = Signal()
    bandsChanged = Signal()
    rmsChanged = Signal()
    peakChanged = Signal()
    diagnosticsChanged = Signal()
    debugOverlayEnabledChanged = Signal()
    _runtimeUpdateAvailable = Signal()

    _MODE_NAMES = ("Reference bars", "Long cats", "Bouncing cats")
    _BAND_COUNT = 24

    def __init__(
        self,
        sources: Sequence[AudioSource],
        analyzer: SpectrumAnalyzer,
        *,
        initial_source_id: str | None = None,
        initial_mode: str | None = None,
        initial_sensitivity: float = 1.0,
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
        self._mode = initial_mode if initial_mode in self._MODE_NAMES else self._MODE_NAMES[0]
        self._sensitivity = min(max(initial_sensitivity, 0.5), 2.0)
        self._running = False
        self._error_state: ControllerErrorState | None = None
        self._bands = [0.0] * self._BAND_COUNT
        self._rms = 0.0
        self._peak = 0.0
        self._frames_per_second = 0.0
        self._processing_time_ms = 0.0
        self._replaced_frames = 0
        self._last_delivery_time: float | None = None
        self._debug_overlay_enabled = False
        self._latest_frame: VisualizerFrame | None = None
        self._worker = self._create_worker()

        self._runtimeUpdateAvailable.connect(
            self.processNextFrame,
            Qt.ConnectionType.QueuedConnection,
        )

    def _create_worker(self) -> AnalysisWorker:
        return AnalysisWorker(
            self._selected_source,
            self._analyzer,
            on_update_available=self._runtimeUpdateAvailable.emit,
        )

    @classmethod
    def mode_names(cls) -> tuple[str, ...]:
        return cls._MODE_NAMES

    def _get_source_names(self) -> list[str]:
        return [source.display_name for source in self._sources]

    sourceNames = Property(list, _get_source_names, constant=True)

    def _get_source(self) -> str:
        return self._selected_source.display_name

    def _set_source(self, value: str) -> None:
        selected_source = self._source_by_name.get(value)
        if selected_source is None or selected_source is self._selected_source:
            return

        was_running = self._running
        self._running = False
        self._worker.shutdown()
        self._selected_source = selected_source
        self._worker = self._create_worker()
        self._reset_output()
        self._set_error_state(None)
        self.sourceChanged.emit()

        if was_running:
            self._worker.start()
            self._running = True

    source = Property(str, _get_source, _set_source, notify=sourceChanged)

    @Property(str, notify=sourceChanged)
    def sourceId(self) -> str:
        return self._selected_source.source_id

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

    @Property(float, notify=diagnosticsChanged)
    def framesPerSecond(self) -> float:
        return self._frames_per_second

    @Property(float, notify=diagnosticsChanged)
    def processingTimeMs(self) -> float:
        return self._processing_time_ms

    @Property(int, notify=diagnosticsChanged)
    def replacedFrames(self) -> int:
        return self._replaced_frames

    def _get_debug_overlay_enabled(self) -> bool:
        return self._debug_overlay_enabled

    def _set_debug_overlay_enabled(self, value: bool) -> None:
        if value == self._debug_overlay_enabled:
            return
        self._debug_overlay_enabled = value
        self.debugOverlayEnabledChanged.emit()

    debugOverlayEnabled = Property(
        bool,
        _get_debug_overlay_enabled,
        _set_debug_overlay_enabled,
        notify=debugOverlayEnabledChanged,
    )

    def _get_bands(self) -> list[float]:
        return list(self._bands)

    bands = Property(list, _get_bands, notify=bandsChanged)

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return "" if self._error_state is None else self._error_state.message

    @Property(str, notify=errorChanged)
    def errorCode(self) -> str:
        return "" if self._error_state is None else self._error_state.code.value

    @property
    def error_state(self) -> ControllerErrorState | None:
        return self._error_state

    @Slot()
    def toggleRunning(self) -> None:
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self) -> None:
        self._reset_output()
        self._reset_diagnostics()
        self._set_error_state(None)
        self._worker.start()
        self._running = True
        self.runningChanged.emit()

    def _stop(self) -> None:
        self._running = False
        self._worker.stop()
        self._reset_output()
        self.runningChanged.emit()

    @Slot()
    def shutdown(self) -> None:
        was_running = self._running
        self._running = False
        self._worker.shutdown()
        self._reset_output()
        if was_running:
            self.runningChanged.emit()

    @Slot()
    def processNextFrame(self) -> None:
        update = self._worker.take_latest()
        if not self._running or update is None:
            return
        if isinstance(update, WorkerFailure):
            self._handle_worker_failure(update)
            return
        self._latest_frame = update
        self._publish_latest_frame()
        self._update_diagnostics()

    def _handle_worker_failure(self, failure: WorkerFailure) -> None:
        self._running = False
        self._worker.stop()
        self._reset_output()
        detail = failure.message or "worker operation failed"
        source_failed = failure.stage in (
            WorkerFailureStage.STARTUP,
            WorkerFailureStage.SOURCE_READ,
        )
        code = (
            ControllerErrorCode.AUDIO_SOURCE_FAILED
            if source_failed
            else ControllerErrorCode.ANALYSIS_WORKER_FAILED
        )
        prefix = f"{self._selected_source.display_name}: " if source_failed else ""
        message = f"{prefix}{failure.stage.value}: {failure.exception_type}: {detail}"
        self._set_error_state(
            ControllerErrorState(
                code=code,
                message=message,
            )
        )
        self.runningChanged.emit()

    def _reset_output(self) -> None:
        self._latest_frame = None
        self._set_output([0.0] * self._BAND_COUNT, 0.0, 0.0)

    def _reset_diagnostics(self) -> None:
        changed = any(
            (
                self._frames_per_second != 0.0,
                self._processing_time_ms != 0.0,
                self._replaced_frames != 0,
            )
        )
        self._frames_per_second = 0.0
        self._processing_time_ms = 0.0
        self._replaced_frames = 0
        self._last_delivery_time = None
        if changed:
            self.diagnosticsChanged.emit()

    def _update_diagnostics(self) -> None:
        delivery_time = perf_counter()
        if self._last_delivery_time is not None:
            elapsed = delivery_time - self._last_delivery_time
            if elapsed > 0.0:
                current_fps = 1.0 / elapsed
                if self._frames_per_second == 0.0:
                    self._frames_per_second = current_fps
                else:
                    self._frames_per_second = self._frames_per_second * 0.8 + current_fps * 0.2
        self._last_delivery_time = delivery_time
        self._processing_time_ms = self._worker.processing_time_ms
        self._replaced_frames = self._worker.replaced_frame_count
        self.diagnosticsChanged.emit()

    def _set_error_state(self, value: ControllerErrorState | None) -> None:
        if value == self._error_state:
            return
        self._error_state = value
        self.errorChanged.emit()

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
