import QtQuick

Item {
    id: root

    required property int index
    required property real bandValue
    required property color fillColor
    required property color borderColor

    objectName: "spectrumBar"

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: Math.max(3, parent.height * root.bandValue)
        color: root.fillColor
        border.color: root.borderColor
        radius: Math.min(width / 2, 6)
    }
}
