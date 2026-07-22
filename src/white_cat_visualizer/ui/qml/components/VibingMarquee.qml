pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls.Basic

Item {
    id: root

    property bool active: false
    property string text: qsTr("Vibing mode")
    property color textColor: "#FFFFFF"
    property color catColor: "#FFFFFF"
    property color trailColor: "#FFFFFF"
    property int trailDotCount: 7
    property real trailLength: 44
    property real catTextGap: 7
    property real pixelsPerSecond: 126

    property real travelProgress: 0.0
    property real trailPhase: 0.0

    readonly property real runnerWidth:
        trailLength + runningCat.width + catTextGap + marqueeLabel.implicitWidth

    clip: true

    Accessible.role: Accessible.StaticText
    Accessible.name: root.text

    function restartAnimations() {
        travelProgress = 0.0
        trailPhase = 0.0
        travelAnimation.restart()
        trailAnimation.restart()
        bobAnimation.restart()
        frontLegAnimation.restart()
        backLegAnimation.restart()
        tailAnimation.restart()
    }

    function stopAnimations() {
        travelAnimation.stop()
        trailAnimation.stop()
        bobAnimation.stop()
        frontLegAnimation.stop()
        backLegAnimation.stop()
        tailAnimation.stop()
        travelProgress = 0.0
        trailPhase = 0.0
        runningCat.bobOffset = 0.0
        frontLeg.rotation = -18
        backLeg.rotation = 18
        catTail.rotation = -18
    }

    onActiveChanged: {
        if (active)
            restartAnimations()
        else
            stopAnimations()
    }

    Component.onCompleted: {
        if (active)
            restartAnimations()
    }

    Item {
        id: runner

        width: root.runnerWidth
        height: parent.height
        x: -width + root.travelProgress * (root.width + width)

        Repeater {
            model: root.trailDotCount

            delegate: Rectangle {
                required property int index

                readonly property real age:
                    (root.trailPhase + index / root.trailDotCount) % 1.0
                readonly property real sizeFactor: 1.0 - age

                x: root.trailLength - 3 - age * root.trailLength
                y: Math.round(
                       runner.height / 2
                       + ((index % 3) - 1) * 3
                       - height / 2
                   )
                width: Math.max(1, 5 * sizeFactor)
                height: width
                opacity: sizeFactor * sizeFactor
                color: root.trailColor
                radius: 0
            }
        }

        Item {
            id: runningCat

            property real bobOffset: 0.0

            x: root.trailLength
            y: Math.round((runner.height - height) / 2 + bobOffset)
            width: 32
            height: 23

            Rectangle {
                id: catTail

                x: 0
                y: 9
                width: 10
                height: 3
                color: root.catColor
                radius: 1.5
                transformOrigin: Item.Right
                rotation: -18
            }

            Rectangle {
                x: 6
                y: 7
                width: 19
                height: 11
                color: root.catColor
                radius: 5
            }

            Rectangle {
                x: 21
                y: 4
                width: 10
                height: 11
                color: root.catColor
                radius: 4
            }

            Rectangle {
                x: 21
                y: 2
                width: 5
                height: 5
                color: root.catColor
                rotation: 45
            }

            Rectangle {
                x: 27
                y: 2
                width: 5
                height: 5
                color: root.catColor
                rotation: 45
            }

            Rectangle {
                x: 28
                y: 8
                width: 1.5
                height: 1.5
                color: "#17131D"
                radius: 0.75
            }

            Rectangle {
                id: backLeg

                x: 9
                y: 15
                width: 3
                height: 7
                color: root.catColor
                radius: 1
                transformOrigin: Item.Top
                rotation: 18
            }

            Rectangle {
                id: frontLeg

                x: 22
                y: 15
                width: 3
                height: 7
                color: root.catColor
                radius: 1
                transformOrigin: Item.Top
                rotation: -18
            }
        }

        Label {
            id: marqueeLabel

            x: runningCat.x + runningCat.width + root.catTextGap
            anchors.verticalCenter: parent.verticalCenter
            text: root.text
            color: root.textColor
            font.pixelSize: 13
            font.weight: Font.DemiBold
            font.letterSpacing: 0.8
            verticalAlignment: Text.AlignVCenter
        }
    }

    NumberAnimation {
        id: travelAnimation

        target: root
        property: "travelProgress"
        from: 0.0
        to: 1.0
        duration: Math.max(
                      4200,
                      Math.round((root.width + runner.width)
                                 / root.pixelsPerSecond * 1000)
                  )
        loops: Animation.Infinite
        easing.type: Easing.Linear
    }

    NumberAnimation {
        id: trailAnimation

        target: root
        property: "trailPhase"
        from: 0.0
        to: 1.0
        duration: 760
        loops: Animation.Infinite
        easing.type: Easing.Linear
    }

    SequentialAnimation {
        id: bobAnimation
        loops: Animation.Infinite

        NumberAnimation {
            target: runningCat
            property: "bobOffset"
            from: 0.0
            to: -2.0
            duration: 105
            easing.type: Easing.OutQuad
        }
        NumberAnimation {
            target: runningCat
            property: "bobOffset"
            from: -2.0
            to: 0.0
            duration: 105
            easing.type: Easing.InQuad
        }
    }

    SequentialAnimation {
        id: frontLegAnimation
        loops: Animation.Infinite

        NumberAnimation {
            target: frontLeg
            property: "rotation"
            from: -24
            to: 24
            duration: 110
            easing.type: Easing.InOutQuad
        }
        NumberAnimation {
            target: frontLeg
            property: "rotation"
            from: 24
            to: -24
            duration: 110
            easing.type: Easing.InOutQuad
        }
    }

    SequentialAnimation {
        id: backLegAnimation
        loops: Animation.Infinite

        NumberAnimation {
            target: backLeg
            property: "rotation"
            from: 24
            to: -24
            duration: 110
            easing.type: Easing.InOutQuad
        }
        NumberAnimation {
            target: backLeg
            property: "rotation"
            from: -24
            to: 24
            duration: 110
            easing.type: Easing.InOutQuad
        }
    }

    SequentialAnimation {
        id: tailAnimation
        loops: Animation.Infinite

        NumberAnimation {
            target: catTail
            property: "rotation"
            from: -24
            to: 4
            duration: 170
            easing.type: Easing.InOutSine
        }
        NumberAnimation {
            target: catTail
            property: "rotation"
            from: 4
            to: -24
            duration: 170
            easing.type: Easing.InOutSine
        }
    }
}
