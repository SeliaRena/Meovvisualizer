pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "components" as Components
import "long_bar_cat" as LongBarCat

ApplicationWindow {
    id: root

    required property var controller
    required property var settingsManager

    Components.VisualTokens {
        id: theme
    }

    FontMetrics {
        id: errorFontMetrics

        font.pixelSize: 12
    }

    FontLoader {
        id: soraFont

        source: "../Sora-Regular.ttf"
    }

    visible: true
    width: Math.max(settingsManager.windowWidth, minimumWidth)
    height: Math.max(settingsManager.windowHeight, minimumHeight)
    minimumWidth: 520
    minimumHeight: Math.max(480, Math.ceil(requiredWindowHeight))
    title: qsTr("Meovvisualizer")
    flags: Qt.Window 
         | Qt.FramelessWindowHint
         | Qt.WindowStaysOnTopHint
    color: "transparent"
    opacity: 1.0

    readonly property int wideToolbarMinimumWidth: 896
    readonly property bool narrow: width < wideToolbarMinimumWidth
    readonly property bool maximized: visibility === Window.Maximized
    readonly property real effectiveOuterInset: maximized ? 0 : theme.outerInset
    readonly property real effectivePanelRadius: maximized ? 0 : theme.panelRadius
    readonly property int resizeHandleThickness: 7
    readonly property int resizeCornerSize: 14

    // Stable vertical contracts.
    //
    // startSystemResize() delegates the interactive resize to Windows. Windows
    // reads the window's minimum tracking size when that operation begins.
    // Therefore the minimum height must remain invariant while the width crosses
    // the wide/narrow breakpoint; a live controlsFlow.implicitHeight value is
    // not suitable for the native minimum-size contract.
    readonly property int titleBarHeight: 36
    readonly property int mainLayoutSpacing: 8
    readonly property int separatorHeight: 1
    readonly property int minimumCanvasHeight: 300
    readonly property int visualizerTopInset: 48
    readonly property int visualizerBottomInset: 12

    readonly property real wideControlsMinimumHeight:
        Math.max(
            sourceGroup.implicitHeight,
            modeGroup.implicitHeight,
            sensitivityGroup.implicitHeight,
            levelGroup.implicitHeight,
            runningGroup.implicitHeight
        )

    readonly property real narrowControlsMinimumHeight:
        Math.max(sourceGroup.implicitHeight, modeGroup.implicitHeight)
        + Math.max(sensitivityGroup.implicitHeight, levelGroup.implicitHeight)
        + runningGroup.implicitHeight
        + 2 * controlsFlow.rowSpacing

    readonly property real reservedErrorHeight:
        Math.max(1, Math.ceil(errorFontMetrics.height))

    readonly property real stableControlsContentMinimumHeight:
        Math.max(wideControlsMinimumHeight, narrowControlsMinimumHeight)
        + controlSurface.spacing
        + reservedErrorHeight

    // The native minimum-size contract always reserves the fully expanded
    // controls panel. Collapsing the panel gives space back to the visualizer,
    // but never allows the window to become too small to expand safely again.
    readonly property real stableControlsMinimumHeight:
        stableControlsContentMinimumHeight
        + controlsPanel.expandedChromeHeight

    readonly property real requiredContentHeight:
        titleBarHeight
        + stableControlsMinimumHeight
        + separatorHeight
        + minimumCanvasHeight
        + 3 * mainLayoutSpacing
        + 2 * theme.panelPadding

    readonly property real requiredWindowHeight:
        requiredContentHeight + 2 * theme.outerInset

    // Compatibility properties retained for tests and diagnostics.
    readonly property real minimumControlsHeight: stableControlsMinimumHeight
    readonly property real controlsContentHeight: controlSurface.implicitHeight
    readonly property real controlsHeight: controlSurface.implicitHeight
    readonly property real controlsPanelHeight: controlsPanel.implicitHeight

    Component.onCompleted: {
        if (settingsManager.hasWindowPosition) {
            root.x = settingsManager.windowX
            root.y = settingsManager.windowY
        }
        sourceControl.forceActiveFocus(Qt.TabFocusReason)
    }
    onClosing: settingsManager.saveWindow(root.x, root.y, root.width, root.height)

    Shortcut {
        sequence: "F12"
        onActivated: root.controller.debugOverlayEnabled = !root.controller.debugOverlayEnabled
    }

    Rectangle {
        id: panelShadow

        objectName: "panelShadow"
        anchors.fill: parent
        anchors.margins: Math.max(0, root.effectiveOuterInset - 2)
        visible: !root.maximized
        color: theme.panelShadow
        radius: root.effectivePanelRadius + 2

        transform: Translate {
            y: 4
        }
    }

    Rectangle {
        id: mainSurface

        objectName: "mainGlassSurface"
        anchors.fill: parent
        anchors.margins: root.effectiveOuterInset
        visible: true
        opacity: 1.0
        color: theme.mainGlass
        border.color: theme.strongBorder
        border.width: root.maximized ? 0 : 1
        radius: root.effectivePanelRadius

        ColumnLayout {
            id: mainLayout

            anchors.fill: parent
            anchors.margins: theme.panelPadding
            spacing: root.mainLayoutSpacing

            Item {
                id: titleBar

                objectName: "titleBar"
                Layout.fillWidth: true
                Layout.minimumHeight: root.titleBarHeight
                Layout.preferredHeight: root.titleBarHeight

                RowLayout {
                    anchors.fill: parent
                    spacing: 6

                    Item {
                        id: titleDragArea

                        objectName: "titleDragArea"
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        Label {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            text: root.title
                            color: theme.primaryText
                            font.pixelSize: 14
                            font.weight: Font.Normal
                            font.family: soraFont.name
                            elide: Text.ElideRight
                        }

                        DragHandler {
                            target: null
                            acceptedButtons: Qt.LeftButton

                            onActiveChanged: {
                                if (active)
                                    root.startSystemMove()
                            }
                        }

                        TapHandler {
                            acceptedButtons: Qt.LeftButton

                            onDoubleTapped: {
                                if (root.maximized)
                                    root.showNormal()
                                else
                                    root.showMaximized()
                            }
                        }
                    }

                    Button {
                        id: minimizeButton

                        objectName: "minimizeButton"
                        Layout.preferredWidth: 38
                        Layout.fillHeight: true
                        activeFocusOnTab: false
                        text: "\u2212"
                        Accessible.name: qsTr("Minimize window")
                        onClicked: root.showMinimized()

                        contentItem: Text {
                            text: minimizeButton.text
                            color: theme.primaryText
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: minimizeButton.down ? theme.pressedOverlay
                                                       : minimizeButton.hovered ? theme.hoverOverlay
                                                                                : "transparent"
                            radius: theme.smallRadius

                            Behavior on color {
                                ColorAnimation { duration: theme.transitionDuration }
                            }
                        }
                    }

                    Button {
                        id: maximizeButton

                        objectName: "maximizeButton"
                        Layout.preferredWidth: 38
                        Layout.fillHeight: true
                        activeFocusOnTab: false
                        text: root.maximized ? "\u2750" : "\u25A1"
                        Accessible.name: root.maximized
                                         ? qsTr("Restore window")
                                         : qsTr("Maximize window")
                        onClicked: {
                            if (root.maximized)
                                root.showNormal()
                            else
                                root.showMaximized()
                        }

                        contentItem: Text {
                            text: maximizeButton.text
                            color: theme.primaryText
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: maximizeButton.down ? theme.pressedOverlay
                                                       : maximizeButton.hovered ? theme.hoverOverlay
                                                                                : "transparent"
                            radius: theme.smallRadius

                            Behavior on color {
                                ColorAnimation { duration: theme.transitionDuration }
                            }
                        }
                    }

                    Button {
                        id: closeButton

                        objectName: "closeButton"
                        Layout.preferredWidth: 38
                        Layout.fillHeight: true
                        activeFocusOnTab: false
                        text: "\u00D7"
                        Accessible.name: qsTr("Close window")
                        onClicked: root.close()

                        contentItem: Text {
                            text: closeButton.text
                            color: theme.primaryText
                            font.pixelSize: 18
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: closeButton.down ? theme.pressedOverlay
                                                    : closeButton.hovered ? theme.hoverOverlay
                                                                          : "transparent"
                            radius: theme.smallRadius

                            Behavior on color {
                                ColorAnimation { duration: theme.transitionDuration }
                            }
                        }
                    }
                }
            }

            Components.ExpandableControlsPanel {
                id: controlsPanel

                objectName: "expandableControlsPanel"
                Layout.fillWidth: true
                Layout.minimumHeight: implicitHeight
                Layout.preferredHeight: implicitHeight
                theme: theme
                expanded: true
                panelTitle: qsTr("CONTROLS")
                marqueeText: qsTr("Vibing mode")

                ColumnLayout {
                    id: controlSurface

                    objectName: "controlSurface"
                    Layout.fillWidth: true
                    Layout.minimumHeight: implicitHeight
                    Layout.preferredHeight: implicitHeight
                    spacing: 8

                    GridLayout {
                        id: controlsFlow

                        objectName: "controlsFlow"
                        Layout.fillWidth: true
                        columns: root.narrow ? 2 : 5
                        columnSpacing: root.narrow ? theme.controlSpacing : 14
                        rowSpacing: 8

                        ColumnLayout {
                            id: sourceGroup

                            Layout.row: 0
                            Layout.column: 0
                            Layout.fillWidth: true
                            Layout.minimumWidth: 150
                            Layout.preferredWidth: 210
                            Layout.alignment: Qt.AlignTop
                            spacing: 5

                            Label {
                                text: qsTr("SOURCE")
                                color: theme.mutedText
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                                font.letterSpacing: 1.2
                            }
                            ComboBox {
                                id: sourceControl

                                objectName: "sourceControl"
                                Layout.fillWidth: true
                                Layout.minimumHeight: 40
                                Layout.preferredHeight: 40
                                model: root.controller.sourceNames
                                currentIndex: Math.max(0, root.controller.sourceNames.indexOf(root.controller.source))
                                activeFocusOnTab: true
                                Accessible.name: qsTr("Audio source")
                                Accessible.description: qsTr("Select the audio input source")
                                KeyNavigation.tab: modeControl
                                onActivated: root.controller.source = currentText

                                contentItem: Text {
                                    objectName: "sourceControlText"
                                    leftPadding: 12
                                    rightPadding: 34
                                    text: sourceControl.displayText
                                    color: sourceControl.enabled ? theme.primaryText : theme.disabledText
                                    font.pixelSize: 13
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                indicator: Text {
                                    x: sourceControl.width - width - 12
                                    height: sourceControl.height
                                    text: "\u2304"
                                    color: sourceControl.enabled ? theme.secondaryText : theme.disabledText
                                    font.pixelSize: 15
                                    verticalAlignment: Text.AlignVCenter
                                }
                                background: Rectangle {
                                    objectName: "sourceControlBackground"
                                    color: !sourceControl.enabled ? theme.elevatedOverlay
                                                                  : sourceControl.down ? theme.pressedOverlay
                                                                                       : sourceControl.hovered ? theme.hoverOverlay
                                                                                                               : theme.elevatedOverlay
                                    border.color: sourceControl.activeFocus ? theme.accent
                                                                            : sourceControl.hovered ? theme.standardBorder
                                                                                                    : theme.subtleBorder
                                    border.width: sourceControl.activeFocus ? 2 : 1
                                    radius: theme.controlRadius

                                    Behavior on color {
                                        ColorAnimation { duration: theme.transitionDuration }
                                    }
                                }
                                delegate: ItemDelegate {
                                    id: sourceOption

                                    required property string modelData
                                    required property int index

                                    width: sourceControl.width
                                    height: 38
                                    highlighted: sourceControl.highlightedIndex === index
                                    contentItem: Text {
                                        leftPadding: 8
                                        text: sourceOption.modelData
                                        color: sourceOption.enabled ? theme.primaryText : theme.disabledText
                                        verticalAlignment: Text.AlignVCenter
                                        elide: Text.ElideRight
                                    }
                                    background: Rectangle {
                                        color: sourceOption.down ? theme.pressedOverlay
                                                                 : sourceOption.highlighted ? theme.hoverOverlay
                                                                                            : "transparent"
                                        border.color: sourceOption.index === sourceControl.currentIndex
                                                      ? theme.softAccent : "transparent"
                                        border.width: sourceOption.index === sourceControl.currentIndex ? 1 : 0
                                        radius: theme.smallRadius
                                    }
                                }
                                popup.background: Rectangle {
                                    color: theme.mainGlassStrong
                                    border.color: theme.standardBorder
                                    radius: theme.controlRadius
                                }
                            }
                        }

                        ColumnLayout {
                            id: modeGroup

                            Layout.row: 0
                            Layout.column: 1
                            Layout.fillWidth: true
                            Layout.minimumWidth: 130
                            Layout.preferredWidth: 170
                            Layout.alignment: Qt.AlignTop
                            spacing: 5

                            Label {
                                text: qsTr("VISUALIZER")
                                color: theme.mutedText
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                                font.letterSpacing: 1.2
                            }
                            ComboBox {
                                id: modeControl

                                objectName: "modeControl"
                                Layout.fillWidth: true
                                Layout.minimumHeight: 40
                                Layout.preferredHeight: 40
                                model: root.controller.modeNames
                                currentIndex: Math.max(0, root.controller.modeNames.indexOf(root.controller.mode))
                                activeFocusOnTab: true
                                Accessible.name: qsTr("Visualizer mode")
                                Accessible.description: qsTr("Select the visualizer appearance")
                                KeyNavigation.tab: sensitivityControl
                                onActivated: root.controller.mode = currentText

                                contentItem: Text {
                                    leftPadding: 12
                                    rightPadding: 34
                                    text: modeControl.displayText
                                    color: modeControl.enabled ? theme.primaryText : theme.disabledText
                                    font.pixelSize: 13
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                indicator: Text {
                                    x: modeControl.width - width - 12
                                    height: modeControl.height
                                    text: "\u2304"
                                    color: modeControl.enabled ? theme.secondaryText : theme.disabledText
                                    font.pixelSize: 15
                                    verticalAlignment: Text.AlignVCenter
                                }
                                background: Rectangle {
                                    color: !modeControl.enabled ? theme.elevatedOverlay
                                                                : modeControl.down ? theme.pressedOverlay
                                                                                   : modeControl.hovered ? theme.hoverOverlay
                                                                                                         : theme.elevatedOverlay
                                    border.color: modeControl.activeFocus ? theme.accent
                                                                          : modeControl.hovered ? theme.standardBorder
                                                                                                : theme.subtleBorder
                                    border.width: modeControl.activeFocus ? 2 : 1
                                    radius: theme.controlRadius

                                    Behavior on color {
                                        ColorAnimation { duration: theme.transitionDuration }
                                    }
                                }
                                delegate: ItemDelegate {
                                    id: modeOption

                                    required property string modelData
                                    required property int index

                                    width: modeControl.width
                                    height: 38
                                    highlighted: modeControl.highlightedIndex === index
                                    contentItem: Text {
                                        leftPadding: 8
                                        text: modeOption.modelData
                                        color: modeOption.enabled ? theme.primaryText : theme.disabledText
                                        verticalAlignment: Text.AlignVCenter
                                        elide: Text.ElideRight
                                    }
                                    background: Rectangle {
                                        color: modeOption.down ? theme.pressedOverlay
                                                               : modeOption.highlighted ? theme.hoverOverlay
                                                                                        : "transparent"
                                        border.color: modeOption.index === modeControl.currentIndex
                                                      ? theme.softAccent : "transparent"
                                        border.width: modeOption.index === modeControl.currentIndex ? 1 : 0
                                        radius: theme.smallRadius
                                    }
                                }
                                popup.background: Rectangle {
                                    color: theme.mainGlassStrong
                                    border.color: theme.standardBorder
                                    radius: theme.controlRadius
                                }
                            }
                        }

                        ColumnLayout {
                            id: sensitivityGroup

                            Layout.row: root.narrow ? 1 : 0
                            Layout.column: root.narrow ? 0 : 2
                            Layout.fillWidth: true
                            Layout.minimumWidth: 120
                            Layout.preferredWidth: 166
                            Layout.alignment: Qt.AlignTop
                            spacing: 5

                            Label {
                                text: qsTr("SENSITIVITY")
                                color: theme.mutedText
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                                font.letterSpacing: 1.2
                            }
                            Slider {
                                id: sensitivityControl

                                objectName: "sensitivityControl"
                                Layout.fillWidth: true
                                Layout.minimumHeight: 40
                                Layout.preferredHeight: 40
                                from: 0.5
                                to: 2.0
                                stepSize: 0.1
                                value: root.controller.sensitivity
                                activeFocusOnTab: true
                                Accessible.name: qsTr("Sensitivity")
                                Accessible.description: qsTr("Adjust visualizer response strength")
                                KeyNavigation.tab: runningControl
                                onMoved: root.controller.sensitivity = value

                                background: Rectangle {
                                    x: sensitivityControl.leftPadding
                                    y: sensitivityControl.topPadding
                                       + sensitivityControl.availableHeight / 2 - height / 2
                                    width: sensitivityControl.availableWidth
                                    height: 3
                                    color: theme.subtleBorder
                                    radius: height / 2

                                    Rectangle {
                                        width: sensitivityControl.visualPosition * parent.width
                                        height: parent.height
                                        color: sensitivityControl.enabled ? theme.softAccent : theme.disabledText
                                        radius: parent.radius
                                    }
                                }
                                handle: Rectangle {
                                    x: sensitivityControl.leftPadding
                                       + sensitivityControl.visualPosition
                                       * (sensitivityControl.availableWidth - width)
                                    y: sensitivityControl.topPadding
                                       + sensitivityControl.availableHeight / 2 - height / 2
                                    implicitWidth: sensitivityControl.hovered ? 16 : 14
                                    implicitHeight: implicitWidth
                                    color: sensitivityControl.enabled ? theme.primaryText : theme.disabledText
                                    border.color: sensitivityControl.activeFocus ? theme.accent
                                                                                 : theme.standardBorder
                                    border.width: sensitivityControl.activeFocus ? 2 : 1
                                    radius: width / 2

                                    Behavior on implicitWidth {
                                        NumberAnimation { duration: theme.transitionDuration }
                                    }
                                }
                            }
                        }

                        ColumnLayout {
                            id: levelGroup

                            Layout.row: root.narrow ? 1 : 0
                            Layout.column: root.narrow ? 1 : 3
                            Layout.fillWidth: true
                            Layout.minimumWidth: 120
                            Layout.preferredWidth: 148
                            Layout.alignment: Qt.AlignTop
                            spacing: 5

                            Label {
                                text: qsTr("LEVEL")
                                color: theme.mutedText
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                                font.letterSpacing: 1.2
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Label {
                                    Layout.preferredWidth: 30
                                    text: qsTr("RMS")
                                    color: theme.mutedText
                                    font.pixelSize: 10
                                }
                                ProgressBar {
                                    id: rmsLevel

                                    objectName: "rmsLevel"
                                    Layout.fillWidth: true
                                    Layout.minimumWidth: 64
                                    value: root.controller.rms
                                    Accessible.name: qsTr("RMS level")

                                    background: Rectangle {
                                        implicitHeight: 5
                                        color: theme.elevatedOverlay
                                        border.color: theme.subtleBorder
                                        radius: height / 2
                                    }
                                    contentItem: Item {
                                        implicitHeight: 5

                                        Rectangle {
                                            width: rmsLevel.visualPosition * parent.width
                                            height: parent.height
                                            color: theme.secondaryText
                                            radius: height / 2
                                        }
                                    }
                                }
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Label {
                                    Layout.preferredWidth: 30
                                    text: qsTr("PEAK")
                                    color: theme.mutedText
                                    font.pixelSize: 10
                                }
                                ProgressBar {
                                    id: peakLevel

                                    objectName: "peakLevel"
                                    Layout.fillWidth: true
                                    Layout.minimumWidth: 64
                                    value: root.controller.peak
                                    Accessible.name: qsTr("Peak level")

                                    background: Rectangle {
                                        implicitHeight: 5
                                        color: theme.elevatedOverlay
                                        border.color: theme.subtleBorder
                                        radius: height / 2
                                    }
                                    contentItem: Item {
                                        implicitHeight: 5

                                        Rectangle {
                                            width: peakLevel.visualPosition * parent.width
                                            height: parent.height
                                            color: theme.primaryText
                                            radius: height / 2
                                        }
                                    }
                                }
                            }
                        }

                        ColumnLayout {
                            id: runningGroup

                            Layout.row: root.narrow ? 2 : 0
                            Layout.column: root.narrow ? 0 : 4
                            Layout.columnSpan: root.narrow ? 2 : 1
                            Layout.fillWidth: true
                            Layout.minimumWidth: 88
                            Layout.preferredWidth: 112
                            Layout.alignment: Qt.AlignTop
                            spacing: 5

                            Label {
                                text: root.controller.running ? qsTr("RUNNING") : qsTr("STOPPED")
                                color: root.controller.running ? theme.softAccent : theme.mutedText
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                                font.letterSpacing: 1.0
                            }
                            Button {
                                id: runningControl

                                objectName: "runningControl"
                                Layout.fillWidth: true
                                Layout.minimumWidth: 88
                                Layout.minimumHeight: 40
                                Layout.preferredHeight: 40
                                text: root.controller.running ? qsTr("Stop") : qsTr("Start")
                                activeFocusOnTab: true
                                Accessible.name: text
                                Accessible.description: qsTr("Start or stop audio visualization")
                                KeyNavigation.tab: sourceControl
                                onClicked: root.controller.toggleRunning()

                                contentItem: Text {
                                    objectName: "runningControlText"
                                    text: runningControl.text
                                    color: runningControl.enabled ? theme.inverseText : theme.disabledText
                                    font.pixelSize: 13
                                    font.weight: Font.DemiBold
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                background: Rectangle {
                                    objectName: "runningControlBackground"
                                    color: !runningControl.enabled ? theme.elevatedOverlay
                                                                   : runningControl.down ? theme.secondaryText
                                                                                         : runningControl.hovered ? theme.primaryText
                                                                                                                  : theme.primaryControl
                                    border.color: runningControl.activeFocus ? theme.accent
                                                                            : theme.standardBorder
                                    border.width: runningControl.activeFocus ? 2 : 1
                                    radius: theme.controlRadius
                                    scale: runningControl.down ? 0.98 : 1.0

                                    Behavior on color {
                                        ColorAnimation { duration: theme.transitionDuration }
                                    }
                                    Behavior on scale {
                                        NumberAnimation { duration: theme.transitionDuration }
                                    }
                                }
                            }
                        }
                    }

                    Label {
                        id: sourceError

                        objectName: "sourceError"
                        Layout.fillWidth: true
                        visible: root.controller.error.length > 0
                        text: qsTr("Source unavailable: %1").arg(root.controller.error)
                        color: theme.secondaryText
                        font.pixelSize: 12
                        elide: Text.ElideRight
                        Accessible.name: qsTr("Audio source error")
                    }
                }

            }

            Rectangle {
                objectName: "sectionSeparator"
                Layout.fillWidth: true
                Layout.minimumHeight: root.separatorHeight
                Layout.preferredHeight: root.separatorHeight
                color: theme.separator
            }

            Rectangle {
                id: canvas

                objectName: "visualizerCanvas"
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: root.minimumCanvasHeight
                Layout.preferredHeight: root.minimumCanvasHeight
                color: theme.canvasTint
                radius: theme.controlRadius
                clip: true

                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 20
                    text: root.controller.mode
                    color: theme.mutedText
                    font.pixelSize: 11
                    font.letterSpacing: 0.5
                }

                Rectangle {
                    anchors.left: visualizerViewport.left
                    anchors.right: visualizerViewport.right
                    anchors.bottom: visualizerViewport.bottom
                    height: 1
                    color: theme.subtleBorder
                }

                Rectangle {
                    id: diagnosticsOverlay

                    objectName: "diagnosticsOverlay"
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 14
                    width: 190
                    height: 76
                    visible: root.controller.debugOverlayEnabled
                    color: theme.mainGlassStrong
                    border.color: theme.standardBorder
                    radius: theme.controlRadius
                    Accessible.name: qsTr("Performance diagnostics")

                    Label {
                        anchors.fill: parent
                        anchors.margins: 10
                        text: qsTr("FPS: %1\nProcessing: %2 ms\nReplaced frames: %3")
                              .arg(root.controller.framesPerSecond.toFixed(1))
                              .arg(root.controller.processingTimeMs.toFixed(2))
                              .arg(root.controller.replacedFrames)
                        color: theme.secondaryText
                        font.family: "Consolas"
                        font.pixelSize: 12
                    }
                }

                Item {
                    id: visualizerViewport

                    objectName: "visualizerViewport"
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: root.narrow ? 14 : 28
                    anchors.rightMargin: root.narrow ? 14 : 28
                    anchors.topMargin: root.visualizerTopInset
                    anchors.bottomMargin: root.visualizerBottomInset
                    clip: true
                }

                Row {
                    id: referenceVisualizer

                    objectName: "referenceVisualizer"
                    anchors.fill: visualizerViewport
                    spacing: Math.max(2, Math.min(6, width / 140))
                    visible: root.controller.mode === "Reference bars"

                    Repeater {
                        objectName: "spectrumBars"
                        model: 24

                        Components.SpectrumBar {
                            width: (referenceVisualizer.width - 23 * referenceVisualizer.spacing) / 24
                            height: parent.height
                            bandValue: root.controller.bands[index]
                            fillColor: theme.catFill
                            borderColor: theme.catDetail
                        }
                    }
                }

                Row {
                    id: longCatVisualizer

                    objectName: "longCatVisualizer"
                    anchors.fill: visualizerViewport
                    spacing: Math.max(2, Math.min(6, width / 140))
                    visible: root.controller.mode === "Long cats"

                    Repeater {
                        objectName: "longCatBars"
                        model: 24

                        LongBarCat.LongCatBar {
                            width: (longCatVisualizer.width - 23 * longCatVisualizer.spacing) / 24
                            height: parent.height
                            bandValue: root.controller.bands[index]
                            transientValue: root.controller.peak
                            peakValue: root.controller.peak
                            fillColor: theme.catFill
                            detailColor: theme.catDetail
                        }
                    }
                }

                Label {
                    anchors.centerIn: parent
                    visible: !root.controller.running
                    text: qsTr("Press Start")
                    color: theme.primaryText
                    font.pixelSize: 13
                }
            }
        }
    }

    Item {
        id: resizeLayer

        objectName: "resizeLayer"
        anchors.fill: parent
        visible: !root.maximized
        z: 1000

        // Edges exclude the corners so each pointer press has one owner.
        MouseArea {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.topMargin: root.resizeCornerSize
            anchors.bottomMargin: root.resizeCornerSize
            width: root.resizeHandleThickness
            cursorShape: Qt.SizeHorCursor
            onPressed: root.startSystemResize(Qt.LeftEdge)
        }

        MouseArea {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.topMargin: root.resizeCornerSize
            anchors.bottomMargin: root.resizeCornerSize
            width: root.resizeHandleThickness
            cursorShape: Qt.SizeHorCursor
            onPressed: root.startSystemResize(Qt.RightEdge)
        }

        MouseArea {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: root.resizeCornerSize
            anchors.rightMargin: root.resizeCornerSize
            height: root.resizeHandleThickness
            cursorShape: Qt.SizeVerCursor
            onPressed: root.startSystemResize(Qt.TopEdge)
        }

        MouseArea {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.leftMargin: root.resizeCornerSize
            anchors.rightMargin: root.resizeCornerSize
            height: root.resizeHandleThickness
            cursorShape: Qt.SizeVerCursor
            onPressed: root.startSystemResize(Qt.BottomEdge)
        }

        MouseArea {
            anchors.left: parent.left
            anchors.top: parent.top
            width: root.resizeCornerSize
            height: root.resizeCornerSize
            cursorShape: Qt.SizeFDiagCursor
            onPressed: root.startSystemResize(Qt.LeftEdge | Qt.TopEdge)
        }

        MouseArea {
            anchors.right: parent.right
            anchors.top: parent.top
            width: root.resizeCornerSize
            height: root.resizeCornerSize
            cursorShape: Qt.SizeBDiagCursor
            onPressed: root.startSystemResize(Qt.RightEdge | Qt.TopEdge)
        }

        MouseArea {
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            width: root.resizeCornerSize
            height: root.resizeCornerSize
            cursorShape: Qt.SizeBDiagCursor
            onPressed: root.startSystemResize(Qt.LeftEdge | Qt.BottomEdge)
        }

        MouseArea {
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            width: root.resizeCornerSize
            height: root.resizeCornerSize
            cursorShape: Qt.SizeFDiagCursor
            onPressed: root.startSystemResize(Qt.RightEdge | Qt.BottomEdge)
        }
    }
}