# White Cat Visualizer

A small Windows desktop music visualizer built with Python 3.11, PySide6/QML, NumPy, and WASAPI loopback. It renders a reference spectrum plus two white-cat visualizers in a compact dark interface. Deterministic synthetic sources are always included, so the application remains usable without audio hardware or the Windows capture dependency.

## Run from source on Windows

In PowerShell from the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[gui,windows-audio]"
white-cat-visualizer
```

Choose an audio source and visualizer, adjust sensitivity, then select **Start**. The source, visualizer, sensitivity, window size, and window position are restored on the next launch. Settings are stored in `%LOCALAPPDATA%\WhiteCatVisualizer\settings.json`.

All controls support keyboard focus and activation. Use Tab and Shift+Tab to move between controls, arrow keys to change combo boxes and sensitivity, and Space or Enter to activate the focused control. F12 toggles the diagnostic overlay; it is always off at startup.

If Windows audio capture is unavailable, the application reports the backend problem and keeps all synthetic sources available. A missing saved audio device, unreadable settings file, or invalid settings value produces a runtime warning and falls back to a safe default rather than preventing startup.

## Verify a development checkout

```powershell
python -m pip install -e ".[dev,gui,windows-audio]"
python scripts/verify.py
python scripts/benchmark_analysis.py
```

The verification command runs formatting, linting, strict type checks, unit and GUI tests, core and GUI smoke tests, and QML linting when Qt's `qmllint` executable is available.

## Build the Windows release folder

Create a clean release environment and run the documented build script:

```powershell
py -3.11 -m venv .venv-release
.\.venv-release\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[release]"
.\scripts\build_windows.ps1
.\dist\WhiteCatVisualizer\WhiteCatVisualizer.exe
```

The default build includes the runtime SVG icon and QML files. To apply a Windows executable icon, supply a project-specific `.ico` file through the build hook:

```powershell
.\scripts\build_windows.ps1 -IconPath .\branding\white-cat.ico
```

The output is an unsigned PyInstaller one-folder application, not an installer. Test the generated executable on the minimum Windows version you intend to support before distribution.

## Known limitations

- Windows capture records the system mix for one selected output endpoint. Per-application capture is not supported.
- Output endpoints are enumerated only at startup. Restart after adding, removing, enabling, or disabling a device.
- The release is not code-signed and has no installer or automatic updater; Windows may display reputation warnings.
- The FPS value is a smoothed UI-delivery estimate. Processing time covers spectrum analysis, and replaced frames count stale worker results discarded during the current run.
- Settings write failures do not interrupt visualization, but changes from that session will not persist.
- There is no recording, cloud sync, plugin system, or alternate theme.
