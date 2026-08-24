from __future__ import annotations

import os
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from threading import Event

import pytest

from white_cat_visualizer.analysis.frame import VisualizerFrame
from white_cat_visualizer.analysis.spectrum import SpectrumAnalyzer
from white_cat_visualizer.audio.frame import AudioFrame
from white_cat_visualizer.audio.source import AudioSource, AudioSourceProvider
from white_cat_visualizer.audio.synthetic import SyntheticAudioSource, SyntheticMode
from white_cat_visualizer.settings import ApplicationSettings, JsonSettingsStore, SettingsManager

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_core = pytest.importorskip("PySide6.QtCore")
qt_gui = pytest.importorskip("PySide6.QtGui")
presentation = pytest.importorskip("white_cat_visualizer.presentation")
QEventLoop = qt_core.QEventLoop
QTimer = qt_core.QTimer
QGuiApplication = qt_gui.QGuiApplication
VisualizerController = presentation.VisualizerController


class TrackingAudioSource:
    def __init__(
        self,
        source_id: str,
        display_name: str,
        *,
        mode: SyntheticMode = SyntheticMode.SEEDED_NOISE,
    ) -> None:
        self._source_id = source_id
        self._display_name = display_name
        self._delegate = SyntheticAudioSource(mode)
        self.reset_count = 0
        self.start_count = 0
        self.stop_count = 0
        self.frame_count = 0

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def display_name(self) -> str:
        return self._display_name

    def reset(self) -> None:
        self.reset_count += 1
        self._delegate.reset()

    def start(self) -> None:
        self.start_count += 1
        self._delegate.start()

    def stop(self) -> None:
        self.stop_count += 1
        self._delegate.stop()

    def next_frame(self) -> AudioFrame:
        self.frame_count += 1
        return self._delegate.next_frame()


class FailingAnalyzer(SpectrumAnalyzer):
    def analyze(self, frame: AudioFrame) -> VisualizerFrame:
        raise RuntimeError(f"failed on frame {frame.frame_index}")


class CountingJsonSettingsStore(JsonSettingsStore):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.save_count = 0

    def save(self, settings: ApplicationSettings) -> bool:
        self.save_count += 1
        return super().save(settings)


@pytest.fixture(scope="module")
def application() -> QGuiApplication:
    existing = QGuiApplication.instance()
    return existing if isinstance(existing, QGuiApplication) else QGuiApplication([])


@pytest.fixture
def make_controller() -> Iterator[
    Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ]
]:
    controllers: list[VisualizerController] = []

    def factory(
        sources: Sequence[AudioSource],
        provider: AudioSourceProvider,
        analyzer: SpectrumAnalyzer | None = None,
    ) -> VisualizerController:
        controller = VisualizerController(
            sources,
            analyzer or SpectrumAnalyzer(),
            initial_source_id=sources[0].source_id,
            audio_source_provider=provider,
        )
        controllers.append(controller)
        return controller

    yield factory
    for controller in controllers:
        controller.shutdown()


def wait_until(predicate: Callable[[], bool]) -> None:
    if predicate():
        return

    loop = QEventLoop()
    poll_timer = QTimer()
    poll_timer.setInterval(0)
    poll_timer.timeout.connect(lambda: loop.quit() if predicate() else None)
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.timeout.connect(loop.quit)
    poll_timer.start()
    timeout_timer.start(1_000)
    loop.exec()
    poll_timer.stop()
    timed_out = not timeout_timer.isActive()
    timeout_timer.stop()

    assert not timed_out, "audio source refresh did not finish"
    assert predicate()


def refresh_and_wait(controller: VisualizerController) -> None:
    controller.refreshAudioSources()
    assert controller.refreshingAudioSources is True
    wait_until(lambda: not controller.refreshingAudioSources)


def test_same_stable_snapshot_is_noop_despite_new_instances_and_order(
    application: QGuiApplication,
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    other = TrackingAudioSource("device:b", "Headphones")
    replacement_current = TrackingAudioSource("device:a", "Speakers")
    replacement_other = TrackingAudioSource("device:b", "Headphones")
    controller = make_controller(
        [current, other],
        lambda: (replacement_other, replacement_current),
        None,
    )
    source_names_changes: list[list[str]] = []
    source_changes: list[str] = []
    controller.sourceNamesChanged.connect(
        lambda: source_names_changes.append(controller.sourceNames)
    )
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))

    refresh_and_wait(controller)

    assert controller.sourceNames == ["Speakers", "Headphones"]
    assert controller.sourceId == "device:a"
    assert source_names_changes == []
    assert source_changes == []
    assert controller.audioSourceRefreshMessage == "No changes detected"
    assert controller.audioSourceRefreshError == ""
    application.processEvents()


def test_changed_snapshot_updates_added_removed_and_renamed_sources(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    removed = TrackingAudioSource("device:b", "Headphones")
    renamed_current = TrackingAudioSource("device:a", "Desk speakers")
    added = TrackingAudioSource("device:c", "Monitor audio")
    controller = make_controller(
        [current, removed],
        lambda: (renamed_current, added),
        None,
    )
    source_names_changes: list[list[str]] = []
    source_changes: list[str] = []
    controller.sourceNamesChanged.connect(
        lambda: source_names_changes.append(controller.sourceNames)
    )
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))

    refresh_and_wait(controller)

    assert controller.sourceNames == ["Desk speakers", "Monitor audio"]
    assert controller.source == "Desk speakers"
    assert controller.sourceId == "device:a"
    assert source_names_changes == [["Desk speakers", "Monitor audio"]]
    assert source_changes == []
    assert controller.audioSourceRefreshMessage == "Audio devices updated"


def test_refresh_does_not_restart_running_source_or_reset_render_state(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    other = TrackingAudioSource("device:b", "Headphones")
    replacement_current = TrackingAudioSource("device:a", "Speakers")
    replacement_other = TrackingAudioSource("device:b", "Headphones")
    added = TrackingAudioSource("device:c", "Monitor audio")
    controller = make_controller(
        [current, other],
        lambda: (replacement_current, replacement_other, added),
        None,
    )
    source_changes: list[str] = []
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands) and controller.processingTimeMs > 0.0)
    lifecycle_before = (
        current.reset_count,
        current.start_count,
        current.stop_count,
    )

    refresh_and_wait(controller)

    assert controller.running is True
    assert controller.sourceId == "device:a"
    assert source_changes == []
    assert (
        current.reset_count,
        current.start_count,
        current.stop_count,
    ) == lifecycle_before
    assert replacement_current.reset_count == 0
    assert replacement_current.start_count == 0
    assert replacement_current.stop_count == 0
    assert any(controller.bands)
    assert controller.rms > 0.0
    assert controller.peak > 0.0
    assert controller.processingTimeMs > 0.0
    assert controller.error == ""
    assert controller.errorCode == ""


def test_removed_current_source_keeps_stream_until_user_selects_another(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    old_other = TrackingAudioSource("device:b", "Headphones")
    refreshed_other = TrackingAudioSource("device:b", "Headphones")
    controller = make_controller(
        [current, old_other],
        lambda: (refreshed_other,),
        None,
    )
    source_changes: list[str] = []
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))
    lifecycle_before = (
        current.reset_count,
        current.start_count,
        current.stop_count,
    )

    refresh_and_wait(controller)

    assert controller.sourceNames == ["Headphones", "Speakers"]
    assert controller.source == "Speakers"
    assert controller.sourceId == "device:a"
    assert controller.running is True
    assert source_changes == []
    assert (
        current.reset_count,
        current.start_count,
        current.stop_count,
    ) == lifecycle_before
    assert any(controller.bands)
    assert (
        controller.audioSourceRefreshMessage
        == "Audio devices updated; current source is no longer listed"
    )

    controller.source = "Headphones"
    wait_until(lambda: refreshed_other.start_count == 1 and any(controller.bands))

    assert controller.sourceId == "device:b"
    assert controller.running is True
    assert current.stop_count > lifecycle_before[2]
    assert refreshed_other.reset_count == 1
    assert refreshed_other.start_count == 1
    assert source_changes == ["device:b"]
    assert controller.sourceNames == ["Headphones"]


def test_selecting_refreshed_object_with_current_source_id_is_noop(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    replacement_current = TrackingAudioSource("device:a", "Renamed speakers")
    other = TrackingAudioSource("device:b", "Headphones")
    controller = make_controller(
        [current],
        lambda: (replacement_current, other),
        None,
    )
    source_changes: list[str] = []
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))
    lifecycle_before = (
        current.reset_count,
        current.start_count,
        current.stop_count,
    )
    refresh_and_wait(controller)

    controller.source = "Renamed speakers"

    assert controller.sourceId == "device:a"
    assert controller.source == "Renamed speakers"
    assert controller.running is True
    assert source_changes == []
    assert (
        current.reset_count,
        current.start_count,
        current.stop_count,
    ) == lifecycle_before
    assert replacement_current.reset_count == 0
    assert replacement_current.start_count == 0
    assert replacement_current.stop_count == 0


def test_enumeration_failure_preserves_catalog_stream_and_runtime_error(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    other = TrackingAudioSource("device:b", "Headphones")

    def failing_provider() -> tuple[AudioSource, ...]:
        raise RuntimeError("endpoint enumeration failed")

    controller = make_controller([current, other], failing_provider, FailingAnalyzer())
    controller.toggleRunning()
    wait_until(lambda: controller.error != "")
    error_before = controller.error
    error_code_before = controller.errorCode
    source_names_before = controller.sourceNames
    lifecycle_before = (
        current.reset_count,
        current.start_count,
        current.stop_count,
    )

    refresh_and_wait(controller)

    assert controller.sourceNames == source_names_before
    assert controller.sourceId == "device:a"
    assert controller.error == error_before
    assert controller.errorCode == error_code_before
    assert (
        current.reset_count,
        current.start_count,
        current.stop_count,
    ) == lifecycle_before
    assert controller.audioSourceRefreshMessage == ""
    assert "endpoint enumeration failed" in controller.audioSourceRefreshError


def test_empty_snapshot_preserves_existing_catalog_and_running_stream(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    other = TrackingAudioSource("device:b", "Headphones")
    controller = make_controller([current, other], tuple, None)
    source_names_changes: list[list[str]] = []
    source_changes: list[str] = []
    controller.sourceNamesChanged.connect(
        lambda: source_names_changes.append(controller.sourceNames)
    )
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))
    controller.toggleRunning()
    wait_until(lambda: any(controller.bands))
    lifecycle_before = (
        current.reset_count,
        current.start_count,
        current.stop_count,
    )

    refresh_and_wait(controller)

    assert controller.sourceNames == ["Speakers", "Headphones"]
    assert controller.sourceId == "device:a"
    assert controller.running is True
    assert source_names_changes == []
    assert source_changes == []
    assert (
        current.reset_count,
        current.start_count,
        current.stop_count,
    ) == lifecycle_before
    assert (
        controller.audioSourceRefreshMessage
        == "No audio output devices were found; existing devices were kept."
    )
    assert controller.audioSourceRefreshError == ""


def test_refresh_does_not_trigger_source_persistence(
    tmp_path: Path,
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    replacement_current = TrackingAudioSource("device:a", "Speakers")
    added = TrackingAudioSource("device:b", "Headphones")
    controller = make_controller(
        [current],
        lambda: (replacement_current, added),
        None,
    )
    store = CountingJsonSettingsStore(tmp_path / "settings.json")
    manager = SettingsManager(store)
    manager.watch_controller(controller)
    source_changes: list[str] = []
    controller.sourceChanged.connect(lambda: source_changes.append(controller.sourceId))

    refresh_and_wait(controller)

    assert source_changes == []
    assert store.save_count == 0
    assert not (tmp_path / "settings.json").exists()


def test_duplicate_refresh_click_is_ignored_while_enumeration_is_running(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    entered = Event()
    release = Event()
    call_count = 0

    def blocking_provider() -> tuple[AudioSource, ...]:
        nonlocal call_count
        call_count += 1
        entered.set()
        assert release.wait(timeout=1.0)
        return (TrackingAudioSource("device:a", "Speakers"),)

    controller = make_controller([current], blocking_provider, None)
    controller.refreshAudioSources()
    assert entered.wait(timeout=1.0)
    try:
        controller.refreshAudioSources()
        assert controller.refreshingAudioSources is True
        assert call_count == 1
    finally:
        release.set()

    wait_until(lambda: not controller.refreshingAudioSources)
    assert call_count == 1
    assert controller.audioSourceRefreshMessage == "No changes detected"


def test_invalid_duplicate_snapshot_is_reported_without_replacing_catalog(
    make_controller: Callable[
        [Sequence[AudioSource], AudioSourceProvider, SpectrumAnalyzer | None],
        VisualizerController,
    ],
) -> None:
    current = TrackingAudioSource("device:a", "Speakers")
    duplicate_a = TrackingAudioSource("device:b", "Duplicate")
    duplicate_b = TrackingAudioSource("device:b", "Duplicate 2")
    controller = make_controller(
        [current],
        lambda: (duplicate_a, duplicate_b),
        None,
    )

    refresh_and_wait(controller)

    assert controller.sourceNames == ["Speakers"]
    assert controller.sourceId == "device:a"
    assert "IDs must be unique" in controller.audioSourceRefreshError
