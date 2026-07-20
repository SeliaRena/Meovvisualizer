from __future__ import annotations

from threading import Event

import numpy as np
import pytest

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.frame import AudioFrame
from white_cat_visualizer.runtime.analysis_worker import (
    AnalysisWorker,
    WorkerFailure,
    WorkerFailureStage,
)


class BurstSource:
    def __init__(self, target_frame_count: int = 20) -> None:
        self.reset_count = 0
        self.start_count = 0
        self.stop_count = 0
        self.frame_count = 0
        self.target_reached = Event()
        self._target_frame_count = target_frame_count

    @property
    def source_id(self) -> str:
        return "test:burst"

    @property
    def display_name(self) -> str:
        return "Test burst"

    def reset(self) -> None:
        self.reset_count += 1
        self.frame_count = 0
        self.target_reached.clear()

    def start(self) -> None:
        self.start_count += 1

    def stop(self) -> None:
        self.stop_count += 1

    def next_frame(self) -> AudioFrame:
        frame_index = self.frame_count
        self.frame_count += 1
        if self.frame_count >= self._target_frame_count:
            self.target_reached.set()
        return AudioFrame(
            samples=np.array([0.25], dtype=np.float32),
            sample_rate=1_000_000_000,
            frame_index=frame_index,
        )


class IndexedAnalyzer(SpectrumAnalyzer):
    def __init__(self) -> None:
        super().__init__()
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1

    def analyze(self, frame: AudioFrame) -> VisualizerFrame:
        value = min((frame.frame_index + 1) / 1_000.0, 1.0)
        return VisualizerFrame(bands=(value,) * 24, rms=value, peak=value)


class FailingAnalyzer(SpectrumAnalyzer):
    def analyze(self, frame: AudioFrame) -> VisualizerFrame:
        raise ValueError(f"cannot analyze frame {frame.frame_index}")


class FailingSource(BurstSource):
    def next_frame(self) -> AudioFrame:
        raise OSError("source disconnected")


def test_worker_coalesces_a_high_rate_source_into_one_pending_update() -> None:
    source = BurstSource(target_frame_count=20)
    notifications: list[None] = []
    worker = AnalysisWorker(
        source,
        IndexedAnalyzer(),
        on_update_available=lambda: notifications.append(None),
    )

    worker.start()
    assert source.target_reached.wait(timeout=1.0)

    assert worker.capacity == 1
    assert notifications == [None]
    update = worker.take_latest()
    assert isinstance(update, VisualizerFrame)
    assert update.rms > 0.001

    worker.stop()
    assert worker.is_running is False


def test_start_stop_restart_and_shutdown_are_idempotent() -> None:
    source = BurstSource()
    analyzer = IndexedAnalyzer()
    update_available = Event()
    worker = AnalysisWorker(source, analyzer, on_update_available=update_available.set)

    worker.start()
    worker.start()
    assert update_available.wait(timeout=1.0)
    assert source.reset_count == 1
    assert source.start_count == 1
    assert analyzer.reset_count == 1

    worker.stop()
    worker.stop()
    assert worker.is_running is False
    assert worker.take_latest() is None

    update_available.clear()
    worker.start()
    assert update_available.wait(timeout=1.0)
    assert source.reset_count == 2
    assert source.start_count == 2
    assert analyzer.reset_count == 2

    worker.shutdown()
    worker.shutdown()
    assert worker.is_running is False
    with pytest.raises(RuntimeError, match="shut down"):
        worker.start()


@pytest.mark.parametrize(
    ("source", "analyzer", "expected_stage", "expected_type"),
    [
        (BurstSource(), FailingAnalyzer(), WorkerFailureStage.ANALYSIS, "ValueError"),
        (FailingSource(), IndexedAnalyzer(), WorkerFailureStage.SOURCE_READ, "OSError"),
    ],
)
def test_worker_publishes_typed_failures(
    source: BurstSource,
    analyzer: SpectrumAnalyzer,
    expected_stage: WorkerFailureStage,
    expected_type: str,
) -> None:
    update_available = Event()
    worker = AnalysisWorker(source, analyzer, on_update_available=update_available.set)

    worker.start()
    assert update_available.wait(timeout=1.0)
    update = worker.take_latest()

    assert isinstance(update, WorkerFailure)
    assert update.stage is expected_stage
    assert update.exception_type == expected_type
    worker.shutdown()


def test_stop_clears_pending_data_and_joins_the_worker() -> None:
    update_available = Event()
    worker = AnalysisWorker(
        BurstSource(),
        IndexedAnalyzer(),
        on_update_available=update_available.set,
    )
    worker.start()
    assert update_available.wait(timeout=1.0)

    worker.stop()

    assert worker.is_running is False
    assert worker.take_latest() is None
