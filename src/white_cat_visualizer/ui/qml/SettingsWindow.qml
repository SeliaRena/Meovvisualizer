pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "components" as Components

ApplicationWindow {
    id: root

    required property var mainWindow

    objectName: "settingsWindow"
    visible: false
    width: 460
    height: 246
    minimumWidth: 460
    maximumWidth: 460
    minimumHeight: 246
    maximumHeight: 246
    title: qsTr("Settings")
    flags: Qt.Dialog 
         | Qt.FramelessWindowHint
         | Qt.WindowStaysOnTopHint
    modality: Qt.NonModal
    transientParent: root.mainWindow
    color: theme.windowClear

    function present() {
        if (!root.visible) {
            root.x = Math.round(
                root.mainWindow.x + (root.mainWindow.width - root.width) / 2
            )
            root.y = Math.round(
                root.mainWindow.y + (root.mainWindow.height - root.height) / 2
            )
        }
        root.show()
        root.raise()
        root.requestActivate()
    }

    Components.VisualTokens {
        id: theme
    }

    FontLoader {
        id: soraFont

        source: "qrc:///qml/Sora-Regular.ttf"
    }

    Shortcut {
        sequence: "Escape"
        context: Qt.WindowShortcut
        enabled: root.visible
        onActivated: root.close()
    }

    Rectangle {
        id: panelShadow

        anchors.fill: parent
        anchors.margins: Math.max(0, theme.outerInset - 2)
        color: theme.panelShadow
        radius: theme.panelRadius + 2

        transform: Translate {
            y: 4
        }
    }

    Rectangle {
        id: settingsSurface

        objectName: "settingsGlassSurface"
        anchors.fill: parent
        anchors.margins: theme.outerInset
        color: theme.mainGlass
        border.color: theme.strongBorder
        border.width: 1
        radius: theme.panelRadius

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: theme.panelPadding
            spacing: 14

            Item {
                id: titleBar

                objectName: "settingsTitleBar"
                Layout.fillWidth: true
                Layout.minimumHeight: 36
                Layout.preferredHeight: 36

                Label {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.title
                    color: theme.primaryText
                    font.family: soraFont.name
                    font.pixelSize: 14
                    font.weight: Font.Normal
                }

                DragHandler {
                    target: null
                    acceptedButtons: Qt.LeftButton

                    onActiveChanged: {
                        if (active)
                            root.startSystemMove()
                    }
                }

                Button {
                    id: closeButton

                    objectName: "settingsCloseButton"
                    anchors.top: parent.top
                    anchors.right: parent.right
                    width: 38
                    height: parent.height
                    activeFocusOnTab: false
                    text: "\u00D7"
                    Accessible.name: qsTr("Close settings")
                    onClicked: root.close()

                    contentItem: Text {
                        text: closeButton.text
                        color: closeButton.enabled ? theme.primaryText : theme.disabledText
                        font.pixelSize: 18
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: !closeButton.enabled ? "transparent"
                                                     : closeButton.down ? theme.pressedOverlay
                                                                        : closeButton.hovered ? theme.hoverOverlay
                                                                                              : "transparent"
                        radius: theme.smallRadius

                        Behavior on color {
                            ColorAnimation { duration: theme.transitionDuration }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.minimumHeight: 1
                Layout.preferredHeight: 1
                color: theme.separator
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 8

                Label {
                    text: qsTr("WINDOW")
                    color: theme.mutedText
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    font.letterSpacing: 1.2
                }

                Rectangle {
                    objectName: "alwaysOnTopSetting"
                    Layout.fillWidth: true
                    Layout.minimumHeight: 86
                    Layout.preferredHeight: 86
                    color: theme.elevatedOverlay
                    border.color: theme.subtleBorder
                    border.width: 1
                    radius: theme.controlRadius

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 14
                        spacing: 16

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Label {
                                Layout.fillWidth: true
                                text: qsTr("Always on top")
                                color: theme.primaryText
                                font.pixelSize: 13
                                font.weight: Font.DemiBold
                            }

                            Label {
                                Layout.fillWidth: true
                                text: qsTr("Keep Meovvisualizer above other windows.")
                                color: theme.secondaryText
                                font.pixelSize: 11
                                wrapMode: Text.WordWrap
                            }
                        }

                        Switch {
                            id: alwaysOnTopSwitch

                            objectName: "alwaysOnTopSwitch"
                            Layout.preferredWidth: 48
                            Layout.preferredHeight: 30
                            activeFocusOnTab: true
                            hoverEnabled: true
                            padding: 0
                            spacing: 0
                            Accessible.name: qsTr("Always on top")
                            Accessible.description:
                                qsTr("Keep Meovvisualizer above other windows.")

                            Binding {
                                target: alwaysOnTopSwitch
                                property: "checked"
                                value: root.mainWindow.windowAlwaysOnTop
                            }

                            onClicked:
                                root.mainWindow.windowAlwaysOnTop =
                                    !root.mainWindow.windowAlwaysOnTop

                            indicator: Item {
                                implicitWidth: 44
                                implicitHeight: 24
                                x: alwaysOnTopSwitch.leftPadding
                                y: alwaysOnTopSwitch.topPadding
                                   + (alwaysOnTopSwitch.availableHeight - height) / 2

                                Rectangle {
                                    anchors.fill: parent
                                    color: !alwaysOnTopSwitch.enabled ? theme.elevatedOverlay
                                                                      : alwaysOnTopSwitch.down ? theme.pressedOverlay
                                                                                               : alwaysOnTopSwitch.checked ? (alwaysOnTopSwitch.hovered ? theme.accent
                                                                                                                                                         : theme.softAccent)
                                                                                                                           : alwaysOnTopSwitch.hovered ? theme.hoverOverlay
                                                                                                                                                       : theme.elevatedOverlay
                                    border.color: alwaysOnTopSwitch.visualFocus ? theme.accent
                                                                                : alwaysOnTopSwitch.hovered ? theme.strongBorder
                                                                                                            : alwaysOnTopSwitch.checked ? theme.standardBorder
                                                                                                                                        : theme.subtleBorder
                                    border.width: alwaysOnTopSwitch.visualFocus ? 2 : 1
                                    radius: height / 2

                                    Behavior on color {
                                        ColorAnimation { duration: theme.transitionDuration }
                                    }

                                    Rectangle {
                                        width: 18
                                        height: 18
                                        x: alwaysOnTopSwitch.checked
                                           ? parent.width - width - 3
                                           : 3
                                        anchors.verticalCenter: parent.verticalCenter
                                        color: alwaysOnTopSwitch.enabled
                                               ? theme.primaryText
                                               : theme.disabledText
                                        border.color: theme.standardBorder
                                        border.width: 1
                                        radius: width / 2
                                        scale: alwaysOnTopSwitch.down ? 0.88 : 1.0

                                        Behavior on x {
                                            NumberAnimation {
                                                duration: theme.transitionDuration
                                                easing.type: Easing.OutCubic
                                            }
                                        }
                                        Behavior on scale {
                                            NumberAnimation { duration: theme.transitionDuration }
                                        }
                                    }
                                }
                            }

                            contentItem: Item {
                                implicitWidth: 0
                                implicitHeight: 0
                            }

                            background: Item {}
                        }
                    }
                }
            }
        }
    }
}
