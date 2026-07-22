import QtQuick

QtObject {
    objectName: "themeTokens"

    readonly property color windowClear: "transparent"
    readonly property color mainGlass: "#C20B0912"
    readonly property color mainGlassStrong: "#DC0D0B16"
    readonly property color secondaryGlass: "#991B1728"
    readonly property color canvasTint: "#24171327"
    readonly property color panelShadow: "#38000000"
    readonly property color primaryControl: "#E8E7EC"
    readonly property color elevatedOverlay: "#1AFFFFFF"
    readonly property color hoverOverlay: "#26FFFFFF"
    readonly property color pressedOverlay: "#38FFFFFF"

    readonly property color strongBorder: "#52FFFFFF"
    readonly property color standardBorder: "#32FFFFFF"
    readonly property color subtleBorder: "#1CFFFFFF"
    readonly property color separator: "#24FFFFFF"

    readonly property color primaryText: "#F7F7FA"
    readonly property color secondaryText: "#BBB8C5"
    readonly property color mutedText: "#85818E"
    readonly property color disabledText: "#5F5B68"
    readonly property color inverseText: "#111016"

    readonly property color accent: "#A491FF"
    readonly property color softAccent: "#709E8CFF"

    // These existing values feed protected visualizer delegates and must not change.
    readonly property color catFill: "#F7F7F5"
    readonly property color catDetail: "#D8D8D4"

    readonly property int panelRadius: 20
    readonly property int controlRadius: 8
    readonly property int smallRadius: 5
    readonly property int outerInset: 12
    readonly property int panelPadding: 16
    readonly property int controlSpacing: 10
    readonly property int transitionDuration: 140
}
