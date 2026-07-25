import PySide6.QtCore          # noqa: F401
import PySide6.QtGui           # noqa: F401
import PySide6.QtNetwork       # noqa: F401
import PySide6.QtQml           # noqa: F401
import PySide6.QtQuick         # noqa: F401
import PySide6.QtQuickControls2  # noqa: F401

from PySide6.QtQuickControls2 import QQuickStyle

QQuickStyle.setStyle("Basic")

from white_cat_visualizer.app import main

if __name__ == "__main__":
    raise SystemExit(main())