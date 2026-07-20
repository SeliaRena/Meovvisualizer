from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
import pytest

import white_cat_visualizer.audio.windows_loopback as windows_loopback
from white_cat_visualizer.audio.windows_loopback import (
    AudioCallback,
    AudioDeviceDisconnectedError,
    BackendSampleFormat,
    ErrorCallback,
    LoopbackBackend,
    WindowsAudioError,
    WindowsAudioUnavailableError,
    WindowsLoopbackAudioSource,
    WindowsOutputEndpoint,
    convert_interleaved_to_mono_float32,
    create_windows_loopback_sources,
    enumerate_windows_output_endpoints,
)

ENDPOINT = WindowsOutputEndpoint(
    source_id="wasapi-loopback:test-device",
    display_name="Test speakers",
    backend_index=7,
    sample_rate=48_000,
    channel_count=2,
)


class FakeStream:
    def __init__(
        self,
        on_start: Callable[[], None],
        *,
        active_after_start: bool = True,
    ) -> None:
        self._on_start = on_start
        self._active_after_start = active_after_start
        self.active = False
        self.start_count = 0
        self.stop_count = 0

    def start(self) -> None:
        self.start_count += 1
        self.active = True
        self._on_start()
        self.active = self._active_after_start

    def stop(self) -> None:
        self.stop_count += 1
        self.active = False

    def is_active(self) -> bool:
        return self.active


class FakeBackend:
    def __init__(
        self,
        *,
        endpoints: Sequence[WindowsOutputEndpoint] = (ENDPOINT,),
        chunks: Sequence[bytes] = (),
        start_error: WindowsAudioError | None = None,
    ) -> None:
        self.endpoints = tuple(endpoints)
        self.chunks = tuple(chunks)
        self.start_error = start_error
        self.stream: FakeStream | None = None
        self.opened_endpoint: WindowsOutputEndpoint | None = None
        self.closed = False

    def enumerate_output_endpoints(self) -> Sequence[WindowsOutputEndpoint]:
        return self.endpoints

    def open_loopback(
        self,
        endpoint: WindowsOutputEndpoint,
        frame_size: int,
        on_audio: AudioCallback,
        on_error: ErrorCallback,
    ) -> FakeStream:
        assert frame_size == 2_048
        self.opened_endpoint = endpoint

        def publish() -> None:
            for chunk in self.chunks:
                on_audio(chunk, endpoint.channel_count, BackendSampleFormat.FLOAT32)
            if self.start_error is not None:
                on_error(self.start_error)

        self.stream = FakeStream(publish)
        return self.stream

    def close(self) -> None:
        self.closed = True


def float_bytes(values: Sequence[float]) -> bytes:
    return np.asarray(values, dtype="<f4").tobytes()


@pytest.mark.parametrize(
    ("data", "sample_format", "expected"),
    [
        (float_bytes([1.0, -1.0, 0.5, 0.25]), BackendSampleFormat.FLOAT32, [0.0, 0.375]),
        (
            np.asarray([32_767, -32_768, 16_384, 0], dtype="<i2").tobytes(),
            BackendSampleFormat.INT16,
            [-1.0 / 65_536.0, 0.25],
        ),
        (
            bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x80]),
            BackendSampleFormat.INT24,
            [-0.5],
        ),
        (
            np.asarray([2_147_483_647, -2_147_483_648], dtype="<i4").tobytes(),
            BackendSampleFormat.INT32,
            [0.0],
        ),
        (bytes([255, 1]), BackendSampleFormat.UINT8, [0.0]),
    ],
)
def test_backend_formats_convert_once_to_mono_contiguous_float32(
    data: bytes,
    sample_format: BackendSampleFormat,
    expected: list[float],
) -> None:
    samples = convert_interleaved_to_mono_float32(
        data,
        channel_count=2,
        sample_format=sample_format,
    )

    assert samples.dtype == np.float32
    assert samples.flags.c_contiguous
    assert np.isfinite(samples).all()
    np.testing.assert_allclose(samples, expected, atol=1e-7)


@pytest.mark.parametrize(
    "data",
    [b"", bytes([0, 0, 0]), float_bytes([1.0, np.nan])],
)
def test_invalid_backend_frames_fail_at_the_conversion_boundary(data: bytes) -> None:
    with pytest.raises(ValueError):
        convert_interleaved_to_mono_float32(
            data,
            channel_count=2,
            sample_format=BackendSampleFormat.FLOAT32,
        )


def test_selected_endpoint_lifecycle_and_callback_handoff_are_bounded() -> None:
    first_chunk = float_bytes([1.0, -1.0, 0.25, 0.75])
    newest_chunk = float_bytes([0.4, 0.2, -0.8, 0.2])
    backend = FakeBackend(chunks=(first_chunk, newest_chunk))
    source = WindowsLoopbackAudioSource(ENDPOINT, backend_factory=lambda: backend)

    source.reset()
    source.start()
    source.start()

    assert backend.opened_endpoint == ENDPOINT
    assert backend.stream is not None
    assert backend.stream.start_count == 1
    assert source.pending_count == 1
    frame = source.next_frame()
    np.testing.assert_allclose(frame.samples, [0.3, -0.3])
    assert frame.frame_index == 1

    source.stop()
    source.stop()
    assert backend.stream.stop_count == 1
    assert backend.closed is True
    with pytest.raises(WindowsAudioError, match="not running"):
        source.next_frame()


def test_device_removal_is_reported_and_a_new_start_can_recover() -> None:
    disconnected = FakeBackend(
        start_error=AudioDeviceDisconnectedError("selected output device was removed")
    )
    recovered = FakeBackend(chunks=(float_bytes([0.5, 0.5]),))
    backends: list[LoopbackBackend] = [disconnected, recovered]
    source = WindowsLoopbackAudioSource(ENDPOINT, backend_factory=lambda: backends.pop(0))

    source.start()
    with pytest.raises(AudioDeviceDisconnectedError, match="removed"):
        source.next_frame()
    source.stop()

    source.reset()
    source.start()
    frame = source.next_frame()
    np.testing.assert_allclose(frame.samples, [0.5])
    source.stop()


def test_enumeration_returns_stable_ids_and_closes_the_backend() -> None:
    backend = FakeBackend()

    endpoints = enumerate_windows_output_endpoints(lambda: backend)

    assert endpoints == (ENDPOINT,)
    assert endpoints[0].source_id == "wasapi-loopback:test-device"
    assert backend.closed is True


def test_duplicate_endpoint_ids_fail_clearly() -> None:
    backend = FakeBackend(endpoints=(ENDPOINT, ENDPOINT))

    with pytest.raises(WindowsAudioError, match="IDs must be unique"):
        enumerate_windows_output_endpoints(lambda: backend)
    assert backend.closed is True


def test_duplicate_endpoint_names_are_labeled_uniquely() -> None:
    endpoints = (
        ENDPOINT,
        WindowsOutputEndpoint(
            source_id="wasapi-loopback:second",
            display_name="Test speakers",
            backend_index=8,
            sample_rate=48_000,
            channel_count=2,
        ),
        WindowsOutputEndpoint(
            source_id="wasapi-loopback:third",
            display_name="Test speakers (2)",
            backend_index=9,
            sample_rate=48_000,
            channel_count=2,
        ),
    )
    backend = FakeBackend(endpoints=endpoints)

    sources = create_windows_loopback_sources(lambda: backend)

    assert [source.display_name for source in sources] == [
        "Test speakers",
        "Test speakers (2)",
        "Test speakers (2) (2)",
    ]


def test_real_backend_is_lazy_and_fails_clearly_off_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(windows_loopback.sys, "platform", "linux")

    with pytest.raises(WindowsAudioUnavailableError, match="only available on Windows"):
        windows_loopback.PyAudioWPatchBackend()
