# Meovvisualizer

### A CAT-driven simple Windows desktop audio visualizer built with Python 3.11, PySide6/QML, NumPy, and WASAPI loopback.
### !! The cats react to the sound you're playing !!

I built this purely for fun. I originally just wanted a project to practice working with AI & make my desktop feel more lively, and this idea just came out of nowhere.

But I ended up liking it quite a bit, so I designed a character, polished the whole thing, and decided to release it.

Deterministic synthetic sources are always included, so the application remains usable without audio hardware or the Windows capture dependency.

Everything is open source except the files in ui/qml/long_bar_cat/ that are related to my character design.

## 0 Budget demo video

https://github.com/user-attachments/assets/2d66c3ab-f810-4cd3-8203-eaf1253518b7

## Installation

### Windows (Currently Windows Only)

1. Download the latest Windows x64 ZIP archive from the [Releases page](https://github.com/SeliaRena/Meovvisualizer/releases/latest).
2. Extract the entire archive.
3. Run `Meovvisualizer.exe`.

> Keep all extracted files together. `Meovvisualizer.exe` depends on the runtime files bundled in the release folder.

No installation, Python environment, or additional dependencies are required. Also, sorry for the messy extracted folder. PySide6's deploy method sure is not really friendly. This is currently the best result I can make.

The executable is currently unsigned, so Windows SmartScreen may display a warning on first launch.

## Usage

Choose an audio source and visualizer, adjust sensitivity, then select **Start**. The source, visualizer, sensitivity, window size, and window position are restored on the next launch. Settings are stored in `%LOCALAPPDATA%\WhiteCatVisualizer\settings.json`.

All controls support keyboard focus and activation. Use Tab and Shift+Tab to move between controls, arrow keys to change combo boxes and sensitivity, and Space or Enter to activate the focused control. F12 toggles the diagnostic overlay; it is always off at startup.

If Windows audio capture is unavailable, the application reports the backend problem and keeps all synthetic sources available. A missing saved audio device, unreadable settings file, or invalid settings value produces a runtime warning and falls back to a safe default rather than preventing startup.

## Known limitations

- Windows capture records the system mix for one selected output endpoint. Per-application capture is not supported.
- Output endpoints are enumerated only at startup. Restart after adding, removing, enabling, or disabling a device.
- The release is not code-signed and has no installer or automatic updater; Windows may display reputation warnings.
- The FPS value is a smoothed UI-delivery estimate. Processing time covers spectrum analysis, and replaced frames count stale worker results discarded during the current run.
- Settings write failures do not interrupt visualization, but changes from that session will not persist.
- There is no recording, cloud sync, plugin system, or alternate theme.
