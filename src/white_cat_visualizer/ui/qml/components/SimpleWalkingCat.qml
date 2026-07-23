pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Shapes

Item {
    id: root

    property bool running: false
    property color fillColor: "#FFFFFF"
    property color outlineColor: "#17152F"
    property color shadeColor: "#CAD3DC"   // Kept for API compatibility.
    property color cheekColor: "#F0A9B5"  // Kept for API compatibility.
    property real animationSpeed: 1.0
    property real phase: 0.0

    /*
     * The proportions intentionally follow the supplied drawing:
     * a tall narrow body, high triangular ears, large separated feet,
     * high-set dot eyes, and a diagonal rounded tail.
     */
    implicitWidth: 58
    implicitHeight: 76
    width: implicitWidth
    height: implicitHeight

    Accessible.role: Accessible.Graphic
    Accessible.name: qsTr("Walking white cat")

    onRunningChanged: {
        if (!running)
            phase = 0.0
    }

    Item {
        id: pose

        anchors.fill: parent
        y: 1 - Math.round(Math.abs(Math.sin(root.phase)) * 1.4)

        /*
         * The tail is behind the body. Its right edge overlaps the body so no
         * seam appears while it swings.
         */
        Rectangle {
            id: tail

            x: -10
            y: 55
            width: 29
            height: 7
            color: root.fillColor
            radius: height / 2
            rotation: 51 + Math.sin(root.phase) * 10
            transformOrigin: Item.Right
            antialiasing: true
        }

        /*
         * The feet retain the previous alternating walk. They are deliberately
         * broad and rounded to match the supplied silhouette.
         */
        Rectangle {
            id: rearFoot

            x: 10 + Math.round(Math.sin(root.phase) * 2.2)
            y: 64 - Math.round(Math.max(0, Math.sin(root.phase)) * 2.2)
            width: 22
            height: 11
            color: root.fillColor
            radius: height / 2
            rotation: -Math.sin(root.phase) * 4
            antialiasing: true
        }

        Rectangle {
            id: frontFoot

            x: 35 - Math.round(Math.sin(root.phase) * 2.2)
            y: 64 - Math.round(Math.max(0, -Math.sin(root.phase)) * 2.2)
            width: 22
            height: 11
            color: root.fillColor
            radius: height / 2
            rotation: Math.sin(root.phase) * 4
            antialiasing: true
        }

        /*
         * One continuous fill path reproduces the hand-drawn silhouette:
         * - ears and body are a single shape;
         * - the ear valley is broad and horizontal;
         * - the shoulders round into long parallel sides;
         * - there is no outline.
         */
        Shape {
            id: bodyShape

            x: 13
            y: 1
            width: 39
            height: 69
            antialiasing: true

            ShapePath {
                strokeColor: "transparent"
                strokeWidth: 0
                fillColor: root.fillColor
                joinStyle: ShapePath.RoundJoin
                capStyle: ShapePath.RoundCap
                startX: 3
                startY: 17

                PathLine {
                    x: 8
                    y: 1
                }
                PathLine {
                    x: 16
                    y: 13
                }
                PathLine {
                    x: 25
                    y: 13
                }
                PathLine {
                    x: 34
                    y: 1
                }
                PathLine {
                    x: 37
                    y: 17
                }
                PathCubic {
                    control1X: 39
                    control1Y: 19
                    control2X: 39
                    control2Y: 21
                    x: 39
                    y: 24
                }
                PathLine {
                    x: 39
                    y: 61
                }
                PathCubic {
                    control1X: 39
                    control1Y: 66
                    control2X: 36
                    control2Y: 69
                    x: 31
                    y: 69
                }
                PathLine {
                    x: 9
                    y: 69
                }
                PathCubic {
                    control1X: 4
                    control1Y: 69
                    control2X: 1
                    control2Y: 66
                    x: 1
                    y: 61
                }
                PathLine {
                    x: 1
                    y: 24
                }
                PathCubic {
                    control1X: 1
                    control1Y: 21
                    control2X: 1
                    control2Y: 19
                    x: 3
                    y: 17
                }
            }
        }

        /*
         * The eyes follow the drawing rather than the earlier compact icon:
         * they sit high on the face, are larger, and have a wide horizontal gap.
         */
        Rectangle {
            x: 24
            y: 23
            width: 6
            height: 6
            color: root.outlineColor
            radius: width / 2
            antialiasing: true
        }

        Rectangle {
            x: 38
            y: 23
            width: 6
            height: 6
            color: root.outlineColor
            radius: width / 2
            antialiasing: true
        }
    }

    NumberAnimation {
        id: walkAnimation

        target: root
        property: "phase"
        from: 0.0
        to: Math.PI * 2
        duration: Math.max(300, Math.round(650 / root.animationSpeed))
        loops: Animation.Infinite
        running: root.running
        easing.type: Easing.Linear
    }
}
