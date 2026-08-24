import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtNetwork
import PySide6.QtQml
import PySide6.QtQuick
import PySide6.QtQuickControls2  # noqa: F401
from PySide6.QtQuickControls2 import QQuickStyle

QQuickStyle.setStyle("Basic")

from white_cat_visualizer.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
