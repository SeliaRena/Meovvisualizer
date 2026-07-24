// SPDX-FileCopyrightText: 2026 Selia Rena
// SPDX-License-Identifier: LicenseRef-Long-Bar-Cat
//
// Part of the official Long Bar Cat character implementation.
// See LICENSES/LicenseRef-Long-Bar-Cat.txt.

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

    // Change only this value to resize the complete cat proportionally.
    property real sizeScale: 0.78

    readonly property real designWidth: 58
    readonly property real designHeight: 76

    implicitWidth: designWidth * sizeScale
    implicitHeight: designHeight * sizeScale
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

        width: root.designWidth
        height: root.designHeight
        scale: root.sizeScale
        transformOrigin: Item.TopLeft

        y: (1 - Math.round(Math.abs(Math.sin(root.phase)) * 1.4))
           * root.sizeScale

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
