from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from threading import Event, Lock, Thread, current_thread

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.source import AudioSource
from white_cat_visualizer.runtime.latest_frame import LatestFrameSlot


class WorkerFailureStage(StrEnum):
    STARTUP = "startup"
    SOURCE_READ = "source-read"
    ANALYSIS = "analysis"


@dataclass(frozen=True, slots=True)
class WorkerFailure:
    stage: WorkerFailureStage
    exception_type: str
    message: str


AnalysisUpdate = VisualizerFrame | WorkerFailure


class AnalysisWorker:
    """Read and analyze one source on a dedicated, explicitly owned thread."""

    def __init__(
        self,
        source: AudioSource,
        analyzer: SpectrumAnalyzer,
        *,
        on_update_available: Callable[[], None] | None = None,
    ) -> None:
        self._source = source
        self._analyzer = analyzer
        self._on_update_available = on_update_available
        self._updates: LatestFrameSlot[AnalysisUpdate] = LatestFrameSlot()
        self._stop_requested = Event()
        self._lifecycle_lock = Lock()
        self._thread: Thread | None = None
        self._shutdown = False

    @property
    def capacity(self) -> int:
        return self._updates.capacity

    @property
    def is_running(self) -> bool:
        with self._lifecycle_lock:
            thread = self._thread
            return thread is not None and thread.is_alive()

    def start(self) -> None:
        with self._lifecycle_lock:
            if self._shutdown:
                raise RuntimeError("analysis worker has been shut down")
            if self._thread is not None and self._thread.is_alive():
                return

            self._updates.clear()
            self._stop_requested.clear()
            thread = Thread(
                target=self._run,
                name="white-cat-analysis",
                daemon=False,
            )
            self._thread = thread
            thread.start()

    def stop(self) -> None:
        with self._lifecycle_lock:
            thread = self._thread
            self._stop_requested.set()

        self._source.stop()
        if thread is not None and thread is not current_thread():
            thread.join()
        self._updates.clear()

    def shutdown(self) -> None:
        with self._lifecycle_lock:
            if self._shutdown:
                return
            self._shutdown = True
        self.stop()

    def take_latest(self) -> AnalysisUpdate | None:
        return self._updates.take()

    def _run(self) -> None:
        try:
            self._source.reset()
            self._analyzer.reset()
            self._source.start()
        except Exception as error:
            self._publish_failure(WorkerFailureStage.STARTUP, error)
            return

        try:
            while not self._stop_requested.is_set():
                try:
                    audio_frame = self._source.next_frame()
                except Exception as error:
                    self._publish_failure(WorkerFailureStage.SOURCE_READ, error)
                    return

                if self._stop_requested.is_set():
                    return

                try:
                    visualizer_frame = self._analyzer.analyze(audio_frame)
                except Exception as error:
                    self._publish_failure(WorkerFailureStage.ANALYSIS, error)
                    return

                if self._stop_requested.is_set():
                    return

                self._publish(visualizer_frame)
                self._stop_requested.wait(audio_frame.duration_seconds)
        finally:
            self._source.stop()

    def _publish_failure(self, stage: WorkerFailureStage, error: Exception) -> None:
        if self._stop_requested.is_set():
            return
        failure = WorkerFailure(
            stage=stage,
            exception_type=type(error).__name__,
            message=str(error),
        )
        self._publish(failure)

    def _publish(self, update: AnalysisUpdate) -> None:
        should_notify = self._updates.publish(update)
        if should_notify and self._on_update_available is not None:
            self._on_update_available()
