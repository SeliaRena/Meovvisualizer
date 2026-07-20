import QtQuick
import QtQuick.Shapes

Item {
    id: root

    required property int index
    required property real bandValue
    required property real peakValue
    required property color fillColor
    required property color detailColor

    readonly property real normalizedBand: Math.max(0, Math.min(1, bandValue))
    readonly property real normalizedPeak: Math.max(0, Math.min(1, peakValue))
    readonly property real headSize: Math.max(7, Math.min(width * 1.12, 25))
    readonly property real earHeight: headSize * 0.28
    readonly property real catHeight: headSize + earHeight
    readonly property real maximumOffset: Math.max(0, height - catHeight - 4)
    readonly property real verticalOffset: normalizedBand * maximumOffset
    readonly property real squashAmount: Math.max(0, normalizedPeak - 0.72) / 0.28
    readonly property real squashScale: 1 - squashAmount * 0.2
    readonly property real headTop: cat.y
    readonly property real headBottom: cat.y + cat.height

    objectName: "bouncingCatHead"

    Item {
        id: cat

        objectName: "bouncingCatFace"
        width: root.headSize
        height: root.catHeight
        x: (root.width - width) / 2
        y: root.height - height - root.verticalOffset

        transform: Scale {
            origin.x: cat.width / 2
            origin.y: cat.height
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

            width: cat.width * 0.46
            height: root.earHeight
            y: 1

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

            width: cat.width * 0.46
            height: root.earHeight
            x: cat.width * 0.54
            y: 1

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
            y: root.earHeight
            width: parent.width
            height: root.headSize
            color: root.fillColor
            border.color: root.detailColor
            radius: width / 2

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: -parent.height * 0.08
                spacing: Math.max(1, parent.width * 0.16)

                Repeater {
                    model: 2

                    Rectangle {
                        width: Math.max(1, parent.parent.width * 0.08)
                        height: width
                        color: root.detailColor
                        radius: width / 2
                    }
                }
            }
        }
    }
}
