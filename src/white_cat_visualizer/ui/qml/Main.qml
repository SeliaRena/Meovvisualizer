import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root

    required property var controller

    visible: true
    width: 960
    height: 720
    minimumWidth: 520
    minimumHeight: 480
    title: qsTr("White Cat Visualizer")
    color: "#F7F7F5"

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
            color: "#FFFFFF"
            border.color: "#DDDDDA"
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
                        color: "#777777"
                    }
                    ComboBox {
                        id: sourceControl

                        objectName: "sourceControl"
                        width: parent.width
                        model: root.controller.sourceNames
                        currentIndex: Math.max(0, root.controller.sourceNames.indexOf(root.controller.source))
                        Accessible.name: qsTr("Audio source")
                        onActivated: root.controller.source = currentText
                    }
                }

                Column {
                    width: root.narrow ? 205 : 180
                    spacing: 5

                    Label {
                        text: qsTr("Visualizer")
                        color: "#777777"
                    }
                    ComboBox {
                        id: modeControl

                        objectName: "modeControl"
                        width: parent.width
                        model: root.controller.modeNames
                        currentIndex: Math.max(0, root.controller.modeNames.indexOf(root.controller.mode))
                        Accessible.name: qsTr("Visualizer mode")
                        onActivated: root.controller.mode = currentText
                    }
                }

                Column {
                    width: root.narrow ? 180 : 180
                    spacing: 5

                    Label {
                        text: qsTr("Sensitivity")
                        color: "#777777"
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
                    }
                }

                Column {
                    width: root.narrow ? 120 : 140
                    spacing: 5

                    Label {
                        text: qsTr("Level")
                        color: "#777777"
                    }
                    ProgressBar {
                        objectName: "levelControl"
                        width: parent.width
                        value: Math.max(root.controller.rms, root.controller.peak)
                        Accessible.name: qsTr("Audio level")
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
                }
            }
        }

        Rectangle {
            id: canvas

            objectName: "visualizerCanvas"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 240
            color: "#EDEDEA"
            border.color: "#DDDDDA"
            radius: 10
            clip: true

            Label {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 24
                text: root.controller.mode
                color: "#777777"
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
                            color: "#FFFFFF"
                            border.color: "#CFCFCC"
                            radius: Math.min(width / 2, 6)
                        }
                    }
                }
            }

            Label {
                anchors.centerIn: parent
                text: root.controller.running ? qsTr("Waiting for audio") : qsTr("Press Start")
                color: "#202020"
            }
        }
    }
}
