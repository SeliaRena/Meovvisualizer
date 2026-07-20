from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from threading import Condition, Lock
from typing import Protocol, cast

import numpy as np
from numpy.typing import NDArray

from white_cat_visualizer.audio.frame import AudioFrame


class WindowsAudioError(RuntimeError):
    """Base error for Windows output loopback failures."""


class WindowsAudioUnavailableError(WindowsAudioError):
    """Raised when WASAPI loopback cannot be loaded on this machine."""


class AudioDeviceDisconnectedError(WindowsAudioError):
    """Raised when the selected output endpoint stops producing audio."""


class BackendSampleFormat(StrEnum):
    FLOAT32 = "float32"
    INT16 = "int16"
    INT24 = "int24"
    INT32 = "int32"
    UINT8 = "uint8"


@dataclass(frozen=True, slots=True)
class WindowsOutputEndpoint:
    """One WASAPI loopback endpoint from a single enumeration snapshot."""

    source_id: str
    display_name: str
    backend_index: int
    sample_rate: int
    channel_count: int


AudioCallback = Callable[[bytes, int, BackendSampleFormat], None]
ErrorCallback = Callable[[WindowsAudioError], None]


class LoopbackStream(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...

    def is_active(self) -> bool: ...


class LoopbackBackend(Protocol):
    def enumerate_output_endpoints(self) -> Sequence[WindowsOutputEndpoint]: ...

    def open_loopback(
        self,
        endpoint: WindowsOutputEndpoint,
        frame_size: int,
        on_audio: AudioCallback,
        on_error: ErrorCallback,
    ) -> LoopbackStream: ...

    def close(self) -> None: ...


BackendFactory = Callable[[], LoopbackBackend]


class _PyAudioStream(Protocol):
    def start_stream(self) -> None: ...

    def stop_stream(self) -> None: ...

    def close(self) -> None: ...

    def is_active(self) -> bool: ...


class _PyAudioContext(Protocol):
    def get_loopback_device_info_generator(self) -> Iterator[Mapping[str, object]]: ...

    def open(self, **kwargs: object) -> _PyAudioStream: ...

    def terminate(self) -> None: ...


class _PyAudioModule(Protocol):
    paFloat32: int
    paContinue: int
    paAbort: int

    def PyAudio(self) -> _PyAudioContext: ...


class _PyAudioLoopbackStream:
    def __init__(self, stream: _PyAudioStream) -> None:
        self._stream = stream
        self._closed = False

    def start(self) -> None:
        self._stream.start_stream()

    def stop(self) -> None:
        if self._closed:
            return
        try:
            if self._stream.is_active():
                self._stream.stop_stream()
        finally:
            try:
                self._stream.close()
            finally:
                self._closed = True

    def is_active(self) -> bool:
        return not self._closed and self._stream.is_active()


def _mapping_int(device: Mapping[str, object], key: str) -> int:
    value = device.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise WindowsAudioError(f"WASAPI endpoint has invalid {key}")
    return int(value)


def _mapping_name(device: Mapping[str, object]) -> str:
    value = device.get("name")
    if not isinstance(value, str) or not value.strip():
        raise WindowsAudioError("WASAPI endpoint has no display name")
    return value.strip()


class PyAudioWPatchBackend:
    """Narrow lazy-loaded adapter around PyAudioWPatch's WASAPI API."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise WindowsAudioUnavailableError(
                "Windows output loopback is only available on Windows"
            )
        try:
            module = importlib.import_module("pyaudiowpatch")
        except ModuleNotFoundError as error:
            raise WindowsAudioUnavailableError(
                "PyAudioWPatch is not installed; install the 'windows-audio' extra"
            ) from error

        self._module = cast(_PyAudioModule, module)
        self._audio = self._module.PyAudio()
        self._closed = False

    def enumerate_output_endpoints(self) -> tuple[WindowsOutputEndpoint, ...]:
        endpoints: list[WindowsOutputEndpoint] = []
        for device in self._audio.get_loopback_device_info_generator():
            backend_index = _mapping_int(device, "index")
            sample_rate = _mapping_int(device, "defaultSampleRate")
            channel_count = _mapping_int(device, "maxInputChannels")
            host_api = _mapping_int(device, "hostApi")
            if sample_rate <= 0 or channel_count <= 0:
                continue
            endpoints.append(
                WindowsOutputEndpoint(
                    source_id=f"wasapi-loopback:{host_api}:{backend_index}",
                    display_name=_mapping_name(device),
                    backend_index=backend_index,
                    sample_rate=sample_rate,
                    channel_count=channel_count,
                )
            )
        return tuple(endpoints)

    def open_loopback(
        self,
        endpoint: WindowsOutputEndpoint,
        frame_size: int,
        on_audio: AudioCallback,
        on_error: ErrorCallback,
    ) -> LoopbackStream:
        if self._closed:
            raise WindowsAudioError("WASAPI backend is closed")

        def callback(
            input_data: bytes | None,
            _frame_count: int,
            _time_info: Mapping[str, float],
            status_flags: int,
        ) -> tuple[None, int]:
            if status_flags:
                on_error(
                    AudioDeviceDisconnectedError(f"WASAPI reported stream status {status_flags}")
                )
                return None, self._module.paAbort
            if input_data is None:
                on_error(AudioDeviceDisconnectedError("WASAPI returned no audio data"))
                return None, self._module.paAbort
            try:
                on_audio(input_data, endpoint.channel_count, BackendSampleFormat.FLOAT32)
            except (TypeError, ValueError) as error:
                on_error(WindowsAudioError(f"invalid WASAPI audio frame: {error}"))
                return None, self._module.paAbort
            return None, self._module.paContinue

        stream = self._audio.open(
            format=self._module.paFloat32,
            channels=endpoint.channel_count,
            rate=endpoint.sample_rate,
            input=True,
            input_device_index=endpoint.backend_index,
            frames_per_buffer=frame_size,
            stream_callback=callback,
            start=False,
        )
        return _PyAudioLoopbackStream(stream)

    def close(self) -> None:
        if self._closed:
            return
        self._audio.terminate()
        self._closed = True


def _decode_int24(data: bytes) -> NDArray[np.float32]:
    packed = np.frombuffer(data, dtype=np.uint8)
    if packed.size % 3:
        raise ValueError("24-bit PCM byte count must be divisible by 3")
    triples = packed.reshape(-1, 3).astype(np.int32)
    values = triples[:, 0] | (triples[:, 1] << 8) | (triples[:, 2] << 16)
    values = np.where(values & 0x800000, values - 0x1000000, values)
    return values.astype(np.float32) / 8_388_608.0


def convert_interleaved_to_mono_float32(
    data: bytes,
    *,
    channel_count: int,
    sample_format: BackendSampleFormat,
) -> NDArray[np.float32]:
    """Convert one interleaved backend buffer at the backend boundary."""
    if channel_count <= 0:
        raise ValueError("channel_count must be positive")
    if not data:
        raise ValueError("audio data must not be empty")

    if sample_format is BackendSampleFormat.FLOAT32:
        decoded = np.frombuffer(data, dtype="<f4").astype(np.float32, copy=False)
    elif sample_format is BackendSampleFormat.INT16:
        decoded = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32_768.0
    elif sample_format is BackendSampleFormat.INT24:
        decoded = _decode_int24(data)
    elif sample_format is BackendSampleFormat.INT32:
        decoded = np.frombuffer(data, dtype="<i4").astype(np.float32) / 2_147_483_648.0
    elif sample_format is BackendSampleFormat.UINT8:
        decoded = (np.frombuffer(data, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"unsupported sample format: {sample_format}")

    if decoded.size % channel_count:
        raise ValueError("interleaved sample count must be divisible by channel_count")
    if not np.isfinite(decoded).all():
        raise ValueError("audio data must contain only finite values")

    frames = decoded.reshape(-1, channel_count)
    mono = frames.mean(axis=1, dtype=np.float32)
    return np.ascontiguousarray(mono, dtype=np.float32)


class WindowsLoopbackAudioSource:
    """Selected-output WASAPI source with a single replaceable callback frame."""

    def __init__(
        self,
        endpoint: WindowsOutputEndpoint,
        *,
        frame_size: int = 2_048,
        backend_factory: BackendFactory = PyAudioWPatchBackend,
    ) -> None:
        if frame_size <= 0:
            raise ValueError("frame_size must be positive")
        self._endpoint = endpoint
        self._frame_size = frame_size
        self._backend_factory = backend_factory
        self._condition = Condition(Lock())
        self._pending_frame: AudioFrame | None = None
        self._failure: WindowsAudioError | None = None
        self._backend: LoopbackBackend | None = None
        self._stream: LoopbackStream | None = None
        self._running = False
        self._frame_index = 0

    @property
    def source_id(self) -> str:
        return self._endpoint.source_id

    @property
    def display_name(self) -> str:
        return self._endpoint.display_name

    @property
    def pending_count(self) -> int:
        with self._condition:
            return int(self._pending_frame is not None)

    def reset(self) -> None:
        with self._condition:
            if self._running:
                raise WindowsAudioError("cannot reset a running WASAPI source")
            self._pending_frame = None
            self._failure = None
            self._frame_index = 0

    def start(self) -> None:
        with self._condition:
            if self._running:
                return
            self._pending_frame = None
            self._failure = None
            self._frame_index = 0

        backend = self._backend_factory()
        try:
            stream = backend.open_loopback(
                self._endpoint,
                self._frame_size,
                self._receive_audio,
                self._receive_error,
            )
        except Exception:
            backend.close()
            raise

        with self._condition:
            self._backend = backend
            self._stream = stream
            self._running = True
        try:
            stream.start()
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        with self._condition:
            stream = self._stream
            backend = self._backend
            self._stream = None
            self._backend = None
            self._running = False
            self._pending_frame = None
            self._condition.notify_all()

        if stream is not None:
            try:
                stream.stop()
            finally:
                if backend is not None:
                    backend.close()
        elif backend is not None:
            backend.close()

    def next_frame(self) -> AudioFrame:
        with self._condition:
            while True:
                if self._failure is not None:
                    raise self._failure
                if self._pending_frame is not None:
                    frame = self._pending_frame
                    self._pending_frame = None
                    return frame
                if not self._running:
                    raise WindowsAudioError("WASAPI source is not running")

                stream = self._stream
                self._condition.wait(timeout=0.25)
                if (
                    self._running
                    and self._pending_frame is None
                    and self._failure is None
                    and stream is not None
                    and not stream.is_active()
                ):
                    self._failure = AudioDeviceDisconnectedError(
                        f"Output device disconnected: {self.display_name}"
                    )

    def _receive_audio(
        self,
        data: bytes,
        channel_count: int,
        sample_format: BackendSampleFormat,
    ) -> None:
        samples = convert_interleaved_to_mono_float32(
            data,
            channel_count=channel_count,
            sample_format=sample_format,
        )
        with self._condition:
            if not self._running:
                return
            frame = AudioFrame(
                samples=samples,
                sample_rate=self._endpoint.sample_rate,
                frame_index=self._frame_index,
            )
            self._frame_index += 1
            self._pending_frame = frame
            self._condition.notify()

    def _receive_error(self, error: WindowsAudioError) -> None:
        with self._condition:
            if not self._running:
                return
            self._failure = error
            self._condition.notify_all()


def enumerate_windows_output_endpoints(
    backend_factory: BackendFactory = PyAudioWPatchBackend,
) -> tuple[WindowsOutputEndpoint, ...]:
    backend = backend_factory()
    try:
        endpoints = tuple(backend.enumerate_output_endpoints())
    finally:
        backend.close()

    source_ids = {endpoint.source_id for endpoint in endpoints}
    if len(source_ids) != len(endpoints):
        raise WindowsAudioError("WASAPI endpoint IDs must be unique")
    return endpoints


def create_windows_loopback_sources(
    backend_factory: BackendFactory = PyAudioWPatchBackend,
) -> tuple[WindowsLoopbackAudioSource, ...]:
    endpoints = enumerate_windows_output_endpoints(backend_factory)
    used_display_names: set[str] = set()
    sources: list[WindowsLoopbackAudioSource] = []
    for endpoint in endpoints:
        display_name = endpoint.display_name
        suffix = 2
        while display_name in used_display_names:
            display_name = f"{endpoint.display_name} ({suffix})"
            suffix += 1
        used_display_names.add(display_name)
        labeled_endpoint = WindowsOutputEndpoint(
            source_id=endpoint.source_id,
            display_name=display_name,
            backend_index=endpoint.backend_index,
            sample_rate=endpoint.sample_rate,
            channel_count=endpoint.channel_count,
        )
        sources.append(
            WindowsLoopbackAudioSource(labeled_endpoint, backend_factory=backend_factory)
        )
    return tuple(sources)
