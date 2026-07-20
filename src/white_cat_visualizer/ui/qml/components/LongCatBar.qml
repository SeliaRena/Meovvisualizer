import QtQuick
import QtQuick.Shapes

Item {
    id: root

    required property int index
    required property real bandValue
    required property real transientValue
    required property real peakValue
    required property color fillColor
    required property color detailColor

    readonly property real normalizedBand: Math.max(0, Math.min(1, bandValue))
    readonly property real normalizedTransient: Math.max(0, Math.min(1, transientValue))
    readonly property real normalizedPeak: Math.max(0, Math.min(1, peakValue))
    readonly property real headSize: Math.max(7, Math.min(width * 1.15, 24))
    readonly property real headOffset: normalizedBand * 4 + normalizedTransient * 8
    readonly property real earAngle: normalizedTransient * 18
    readonly property real squashAmount: Math.max(0, normalizedPeak - 0.72) / 0.28
    readonly property real squashScale: 1 - squashAmount * 0.18
    readonly property real minimumBodyHeight: Math.max(7, width * 0.55)
    readonly property real maximumBodyHeight: Math.max(
        minimumBodyHeight,
        height - headSize - 16
    )
    readonly property real bodyHeight: minimumBodyHeight
                                            + normalizedBand
                                            * (maximumBodyHeight - minimumBodyHeight)
    readonly property real headTop: head.y
    readonly property real bodyTop: body.y

    objectName: "longCatBar"

    Rectangle {
        id: body

        objectName: "longCatBody"
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.max(5, root.width * 0.66)
        height: root.bodyHeight
        color: root.fillColor
        radius: Math.min(width / 2, 7)
    }

    Item {
        id: head

        objectName: "longCatHead"
        width: root.headSize
        height: root.headSize
        x: (root.width - width) / 2
        y: Math.max(7, body.y - height - root.headOffset + 3)

        transform: Scale {
            origin.x: head.width / 2
            origin.y: head.height
            xScale: 2 - root.squashScale
            yScale: root.squashScale

            Behavior on xScale {
                NumberAnimation { duration: 90 }
            }
            Behavior on yScale {
                NumberAnimation { duration: 90 }
            }
        }

        Shape {
            id: leftEar

            width: head.width * 0.46
            height: head.height * 0.45
            x: -head.width * 0.01
            y: -height * 0.43

            transform: Rotation {
                origin.x: head.width * 0.23
                origin.y: head.height * 0.45
                angle: -root.earAngle
            }

            ShapePath {
                fillColor: root.fillColor
                strokeColor: root.detailColor
                strokeWidth: 1
                startX: 0
                startY: leftEar.height
                PathLine { x: leftEar.width * 0.45; y: 0 }
                PathLine { x: leftEar.width; y: leftEar.height }
                PathLine { x: 0; y: leftEar.height }
            }
        }

        Shape {
            id: rightEar

            width: head.width * 0.46
            height: head.height * 0.45
            x: head.width * 0.55
            y: -height * 0.43

            transform: Rotation {
                origin.x: head.width * 0.23
                origin.y: head.height * 0.45
                angle: root.earAngle
            }

            ShapePath {
                fillColor: root.fillColor
                strokeColor: root.detailColor
                strokeWidth: 1
                startX: 0
                startY: rightEar.height
                PathLine { x: rightEar.width * 0.55; y: 0 }
                PathLine { x: rightEar.width; y: rightEar.height }
                PathLine { x: 0; y: rightEar.height }
            }
        }

        Rectangle {
            anchors.fill: parent
            color: root.fillColor
            border.color: root.detailColor
            radius: width / 2
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -head.height * 0.08
            spacing: Math.max(1, head.width * 0.16)

            Repeater {
                model: 2

                Rectangle {
                    width: Math.max(1, head.width * 0.08)
                    height: width
                    color: root.detailColor
                    radius: width / 2
                }
            }
        }
    }
}
