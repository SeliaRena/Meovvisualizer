// SPDX-FileCopyrightText: 2026 selia rena
// SPDX-License-Identifier: LicenseRef-Long-Bar-Cat
//
// Part of the official Long Bar Cat character implementation.
// See LICENSES/LicenseRef-Long-Bar-Cat.txt.

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

    readonly property real normalizedBand:
        Math.max(0, Math.min(1, bandValue))

    readonly property real normalizedTransient:
        Math.max(0, Math.min(1, transientValue))

    readonly property real normalizedPeak:
        Math.max(0, Math.min(1, peakValue))

    /*
     * The whole cat has one consistent width.
     * There is no separate wider head or narrower body.
     */
    readonly property real catWidth:
        Math.max(10, width * 0.90)

    readonly property real earHeight:
        catWidth * 0.34

    readonly property real visibleEarHeight:
        earHeight * 0.72

    readonly property real maximumCatHeight:
        Math.max(
            1,
            height - visibleEarHeight - 2
        )

    readonly property real minimumCatHeight:
        Math.min(
            maximumCatHeight,
            Math.max(11, catWidth * 1.10)
        )

    readonly property real catHeight:
        minimumCatHeight
        + normalizedBand
        * (maximumCatHeight - minimumCatHeight)

    /*
     * Peak animation.
     *
     * The whole rounded rectangle softly squashes from the bottom,
     * preserving the smooth movement of the previous version.
     */
    readonly property real squashAmount:
        Math.max(0, normalizedPeak - 0.72) / 0.28

    readonly property real squashXScale:
        1 + squashAmount * 0.12

    readonly property real squashYScale:
        1 - squashAmount * 0.12

    readonly property real earAngle:
        normalizedTransient * 11

    readonly property real earSpread:
        normalizedTransient * catWidth * 0.025

    /*
     * Compatibility properties.
     */
    readonly property real headSize:
        catWidth

    readonly property real headTop:
        cat.y - visibleEarHeight

    readonly property real bodyTop:
        cat.y

    readonly property real bodyHeight:
        catHeight

    objectName: "longCatBar"

    Item {
        id: cat

        width: root.catWidth
        height: root.catHeight

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter

        transformOrigin: Item.Bottom

        transform: Scale {
            origin.x: cat.width / 2
            origin.y: cat.height

            xScale: root.squashXScale
            yScale: root.squashYScale

            Behavior on xScale {
                NumberAnimation {
                    duration: 90
                    easing.type: Easing.OutQuad
                }
            }

            Behavior on yScale {
                NumberAnimation {
                    duration: 90
                    easing.type: Easing.OutQuad
                }
            }
        }

        Behavior on height {
            NumberAnimation {
                duration: 80
                easing.type: Easing.OutQuad
            }
        }

        /*
         * The ears are drawn first.
         *
         * Their lower parts extend behind the rounded rectangle,
         * so their bottom edges are hidden and they appear to grow
         * naturally from the cat's head.
         */
        Item {
            id: leftEar

            width: cat.width * 0.36
            height: root.earHeight

            x: cat.width * 0.09 - root.earSpread
            y: -root.visibleEarHeight

            transformOrigin: Item.Bottom

            rotation: -root.earAngle

            Behavior on rotation {
                NumberAnimation {
                    duration: 80
                    easing.type: Easing.OutQuad
                }
            }

            Behavior on x {
                NumberAnimation {
                    duration: 80
                    easing.type: Easing.OutQuad
                }
            }

            Shape {
                anchors.fill: parent
                antialiasing: true

                ShapePath {
                    fillColor: root.fillColor
                    strokeColor: root.fillColor
                    strokeWidth: Math.max(
                        1,
                        Math.min(1.6, cat.width * 0.06)
                    )

                    joinStyle: ShapePath.RoundJoin

                    startX: 0
                    startY: leftEar.height

                    PathLine {
                        x: leftEar.width * 0.43
                        y: 0
                    }

                    PathLine {
                        x: leftEar.width
                        y: leftEar.height
                    }

                    PathLine {
                        x: 0
                        y: leftEar.height
                    }
                }
            }
        }

        Item {
            id: rightEar

            width: cat.width * 0.36
            height: root.earHeight

            x: cat.width * 0.55 + root.earSpread
            y: -root.visibleEarHeight

            transformOrigin: Item.Bottom

            rotation: root.earAngle

            Behavior on rotation {
                NumberAnimation {
                    duration: 80
                    easing.type: Easing.OutQuad
                }
            }

            Behavior on x {
                NumberAnimation {
                    duration: 80
                    easing.type: Easing.OutQuad
                }
            }

            Shape {
                anchors.fill: parent
                antialiasing: true

                ShapePath {
                    fillColor: root.fillColor
                    strokeColor: root.fillColor
                    strokeWidth: Math.max(
                        1,
                        Math.min(1.6, cat.width * 0.06)
                    )

                    joinStyle: ShapePath.RoundJoin

                    startX: 0
                    startY: rightEar.height

                    PathLine {
                        x: rightEar.width * 0.57
                        y: 0
                    }

                    PathLine {
                        x: rightEar.width
                        y: rightEar.height
                    }

                    PathLine {
                        x: 0
                        y: rightEar.height
                    }
                }
            }
        }

        /*
         * This rectangle is simultaneously the head and body.
         *
         * Because its width never changes along its height,
         * the result looks like a long rounded rectangle rather
         * than a head attached to a narrow neck.
         */
        Rectangle {
            id: body

            objectName: "longCatBody"

            anchors.fill: parent

            color: root.fillColor

            border.color: root.fillColor
            border.width: Math.max(
                1,
                Math.min(1.6, width * 0.06)
            )

            /*
             * The radius depends on width rather than height.
             * A tall cat therefore remains a rounded rectangle
             * instead of turning into an ellipse.
             */
            radius: Math.min(
                width * 0.28,
                8
            )

            antialiasing: true
        }

        /*
         * The face stays close to the top of the rectangle,
         * regardless of how tall the bar becomes.
         */
        Item {
            id: face

            objectName: "longCatHead"

            width: cat.width
            height: cat.width * 0.50

            y: cat.width * 0.13

            /*
             * Large circular eyes create the blank, slightly
             * confused expression from the reference image.
             */
            Rectangle {
                id: leftEye

                width: Math.max(1.8, face.width * 0.16)
                height: width

                x: face.width * 0.245
                y: face.width * 0.105

                color: root.detailColor
                radius: width / 2

                antialiasing: true
            }

            Rectangle {
                id: rightEye

                width: Math.max(1.8, face.width * 0.16)
                height: width

                x: face.width * 0.61
                y: face.width * 0.105

                color: root.detailColor
                radius: width / 2

                antialiasing: true
            }
        }
    }
}