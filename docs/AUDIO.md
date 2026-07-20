# Audio contract and working notes

## Minimal model

PCM is a stream of samples. Convert device input once, at the backend boundary, to mono contiguous `float32`. The analyzer must not understand device channel layouts or integer PCM formats.

Default harness values:

- sample rate: 48,000 Hz when synthetic
- frame size: 2,048 samples
- FFT: `numpy.fft.rfft`
- window: Hann
- bands: 24 logarithmic bands
- visual range: 40 Hz to `min(16 kHz, Nyquist)`
- dB range: -80 dB to 0 dB
- attack: 0.80
- release: 0.20

These are visible configuration defaults, not hidden magic numbers.

## Analyzer order

1. Validate `AudioFrame`.
2. Reuse a cached Hann window for the frame size.
3. Run the real FFT and compute magnitude.
4. Map bins into logarithmic frequency bands.
5. Convert magnitude to a normalized dB value in `[0, 1]`.
6. Apply faster attack and slower release.
7. Compute normalized RMS and peak.
8. Return `VisualizerFrame`.

No output may contain NaN or infinity.

## Deterministic harness

Synthetic modes are the reference inputs for all later layers:

- silence
- sine
- bass pulse
- frequency sweep
- impulse
- seeded noise

A reset with the same seed must reproduce the same frames. Tests use synthetic input, never physical devices.

## Thread and callback rules

- The audio callback performs only unavoidable conversion/copy and bounded publication.
- No UI calls, FFT, file access, network access, per-frame logs, or blocking waits in the callback.
- Use a single newest-frame slot or another fixed-capacity handoff.
- Dropping stale frames is expected when the consumer falls behind.

## Windows backend

The first real backend is selected-output-device WASAPI loopback. It must:

- enumerate stable source IDs and display names
- convert interleaved backend samples to mono `float32`
- expose start, stop, and failure state clearly
- survive repeated start/stop
- report device removal instead of silently freezing
- remain replaceable by `SyntheticAudioSource`

Do not claim per-application capture.

### Manual Windows loopback check

Install the GUI and Windows audio extras, then start the application while audio is playing:

```powershell
python -m pip install -e ".[gui,windows-audio]"
white-cat-visualizer
```

Select each listed Windows output endpoint and confirm that Start animates the level and bands.
Change endpoints and use Start/Stop repeatedly. While a Windows endpoint is selected, disable or
unplug it and confirm the visualizer stops with a visible source error. Re-enable the endpoint,
restart the application if Windows assigned a new endpoint, and confirm Start recovers capture.
Synthetic sources must remain selectable throughout this check.

## Performance rule

Use NumPy vectorization and cache stable arrays. Run `scripts/benchmark_analysis.py` after changing spectrum or smoothing code. Treat a regression as a reason to inspect the hot path, not as permission to introduce opaque code without evidence.
