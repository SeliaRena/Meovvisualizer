import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: root

    required property var controller

    readonly property QtObject theme: QtObject {
        objectName: "themeTokens"

        readonly property color appBackground: "#0D0D0F"
        readonly property color controlSurface: "#161619"
        readonly property color visualizerCanvas: "#111113"
        readonly property color elevatedSurface: "#202024"
        readonly property color hoverSurface: "#29292E"
        readonly property color primaryText: "#F5F5F5"
        readonly property color secondaryText: "#A1A1AA"
        readonly property color mutedText: "#6F6F78"
        readonly property color border: "#303036"
        readonly property color catFill: "#F7F7F5"
        readonly property color catDetail: "#D8D8D4"
        readonly property color disabledContent: "#55555D"
    }

    visible: true
    width: 960
    height: 720
    minimumWidth: 520
    minimumHeight: 480
    title: qsTr("White Cat Visualizer")
    color: theme.appBackground

    readonly property bool narrow: width < 760
    readonly property real controlsHeight: narrow ? 188 : Math.max(132, Math.min(height * 0.2, 170))

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Rectangle {
            id: controlSurface

            objectName: "controlSurface"
            Layout.fillWidth: true
            Layout.preferredHeight: root.controlsHeight
            Layout.minimumHeight: root.controlsHeight
            color: root.theme.controlSurface
            border.color: root.theme.border
            radius: 10

            Flow {
                anchors.fill: parent
                anchors.margins: 14
                spacing: root.narrow ? 10 : 14

                Column {
                    width: root.narrow ? 205 : 190
                    spacing: 5

                    Label {
                        text: qsTr("Source")
                        color: root.theme.secondaryText
                    }
                    ComboBox {
                        id: sourceControl

                        objectName: "sourceControl"
                        width: parent.width
                        model: root.controller.sourceNames
                        currentIndex: Math.max(0, root.controller.sourceNames.indexOf(root.controller.source))
                        Accessible.name: qsTr("Audio source")
                        onActivated: root.controller.source = currentText

                        contentItem: Text {
                            leftPadding: 12
                            rightPadding: 34
                            text: sourceControl.displayText
                            color: sourceControl.enabled ? root.theme.primaryText : root.theme.disabledContent
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                        indicator: Text {
                            x: sourceControl.width - width - 12
                            height: sourceControl.height
                            text: "⌄"
                            color: sourceControl.enabled ? root.theme.secondaryText : root.theme.disabledContent
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: sourceControl.down ? root.theme.border
                                                      : sourceControl.hovered ? root.theme.hoverSurface
                                                                              : root.theme.elevatedSurface
                            border.color: sourceControl.activeFocus ? root.theme.primaryText : root.theme.border
                            radius: 6
                        }
                        delegate: ItemDelegate {
                            required property string modelData
                            required property int index

                            width: sourceControl.width
                            highlighted: sourceControl.highlightedIndex === index
                            contentItem: Text {
                                text: modelData
                                color: root.theme.primaryText
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                            }
                            background: Rectangle {
                                color: parent.highlighted ? root.theme.hoverSurface
                                                          : root.theme.elevatedSurface
                            }
                        }
                        popup.background: Rectangle {
                            color: root.theme.elevatedSurface
                            border.color: root.theme.border
                            radius: 6
                        }
                    }
                }

                Column {
                    width: root.narrow ? 205 : 180
                    spacing: 5

                    Label {
                        text: qsTr("Visualizer")
                        color: root.theme.secondaryText
                    }
                    ComboBox {
                        id: modeControl

                        objectName: "modeControl"
                        width: parent.width
                        model: root.controller.modeNames
                        currentIndex: Math.max(0, root.controller.modeNames.indexOf(root.controller.mode))
                        Accessible.name: qsTr("Visualizer mode")
                        onActivated: root.controller.mode = currentText

                        contentItem: Text {
                            leftPadding: 12
                            rightPadding: 34
                            text: modeControl.displayText
                            color: modeControl.enabled ? root.theme.primaryText : root.theme.disabledContent
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                        indicator: Text {
                            x: modeControl.width - width - 12
                            height: modeControl.height
                            text: "⌄"
                            color: modeControl.enabled ? root.theme.secondaryText : root.theme.disabledContent
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: modeControl.down ? root.theme.border
                                                    : modeControl.hovered ? root.theme.hoverSurface
                                                                          : root.theme.elevatedSurface
                            border.color: modeControl.activeFocus ? root.theme.primaryText : root.theme.border
                            radius: 6
                        }
                        delegate: ItemDelegate {
                            required property string modelData
                            required property int index

                            width: modeControl.width
                            highlighted: modeControl.highlightedIndex === index
                            contentItem: Text {
                                text: modelData
                                color: root.theme.primaryText
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                            }
                            background: Rectangle {
                                color: parent.highlighted ? root.theme.hoverSurface
                                                          : root.theme.elevatedSurface
                            }
                        }
                        popup.background: Rectangle {
                            color: root.theme.elevatedSurface
                            border.color: root.theme.border
                            radius: 6
                        }
                    }
                }

                Column {
                    width: root.narrow ? 180 : 180
                    spacing: 5

                    Label {
                        text: qsTr("Sensitivity")
                        color: root.theme.secondaryText
                    }
                    Slider {
                        id: sensitivityControl

                        objectName: "sensitivityControl"
                        width: parent.width
                        from: 0.5
                        to: 2.0
                        stepSize: 0.1
                        value: root.controller.sensitivity
                        Accessible.name: qsTr("Sensitivity")
                        onMoved: root.controller.sensitivity = value

                        background: Rectangle {
                            x: sensitivityControl.leftPadding
                            y: sensitivityControl.topPadding
                               + sensitivityControl.availableHeight / 2 - height / 2
                            width: sensitivityControl.availableWidth
                            height: 4
                            color: root.theme.border
                            radius: 2

                            Rectangle {
                                width: sensitivityControl.visualPosition * parent.width
                                height: parent.height
                                color: sensitivityControl.enabled ? root.theme.catDetail
                                                                  : root.theme.disabledContent
                                radius: parent.radius
                            }
                        }
                        handle: Rectangle {
                            x: sensitivityControl.leftPadding
                               + sensitivityControl.visualPosition
                               * (sensitivityControl.availableWidth - width)
                            y: sensitivityControl.topPadding
                               + sensitivityControl.availableHeight / 2 - height / 2
                            implicitWidth: 18
                            implicitHeight: 18
                            color: sensitivityControl.enabled ? root.theme.catFill
                                                              : root.theme.disabledContent
                            border.color: sensitivityControl.activeFocus ? root.theme.primaryText
                                                                         : root.theme.border
                            border.width: sensitivityControl.activeFocus ? 2 : 1
                            radius: width / 2
                        }
                    }
                }

                Column {
                    width: root.narrow ? 120 : 140
                    spacing: 5

                    Label {
                        text: qsTr("Level")
                        color: root.theme.secondaryText
                    }
                    ProgressBar {
                        id: levelControl

                        objectName: "levelControl"
                        width: parent.width
                        value: Math.max(root.controller.rms, root.controller.peak)
                        Accessible.name: qsTr("Audio level")

                        background: Rectangle {
                            implicitHeight: 8
                            color: root.theme.elevatedSurface
                            border.color: root.theme.border
                            radius: 4
                        }
                        contentItem: Item {
                            implicitHeight: 8

                            Rectangle {
                                width: levelControl.visualPosition * parent.width
                                height: parent.height
                                color: levelControl.enabled ? root.theme.catDetail
                                                            : root.theme.disabledContent
                                radius: 4
                            }
                        }
                    }
                }

                Button {
                    id: runningControl

                    objectName: "runningControl"
                    width: root.narrow ? 110 : 112
                    height: 48
                    text: root.controller.running ? qsTr("Stop") : qsTr("Start")
                    Accessible.name: text
                    onClicked: root.controller.toggleRunning()

                    contentItem: Text {
                        text: runningControl.text
                        color: runningControl.enabled ? root.theme.primaryText
                                                      : root.theme.disabledContent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: !runningControl.enabled ? root.theme.controlSurface
                                                      : runningControl.down ? root.theme.border
                                                                            : runningControl.hovered ? root.theme.hoverSurface
                                                                                                     : root.theme.elevatedSurface
                        border.color: runningControl.activeFocus ? root.theme.primaryText
                                                                 : root.theme.border
                        border.width: runningControl.activeFocus ? 2 : 1
                        radius: 6
                    }
                }
            }
        }

        Rectangle {
            id: canvas

            objectName: "visualizerCanvas"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 240
            color: root.theme.visualizerCanvas
            border.color: root.theme.border
            radius: 10
            clip: true

            Label {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 24
                text: root.controller.mode
                color: root.theme.mutedText
            }

            Row {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 28
                height: Math.max(80, parent.height - 90)
                spacing: 4

                Repeater {
                    model: root.controller.bands.length

                    Item {
                        required property int index

                        width: Math.max(3, (canvas.width - 56 - 23 * 4) / 24)
                        height: parent.height

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: Math.max(3, parent.height * root.controller.bands[index])
                            color: root.theme.catFill
                            border.color: root.theme.catDetail
                            radius: Math.min(width / 2, 6)
                        }
                    }
                }
            }

            Label {
                anchors.centerIn: parent
                text: root.controller.running ? qsTr("Waiting for audio") : qsTr("Press Start")
                color: root.theme.primaryText
            }
        }
    }
}
