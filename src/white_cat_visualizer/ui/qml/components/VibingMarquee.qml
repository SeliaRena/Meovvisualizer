pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls.Basic
import "../long_bar_cat" as LongBarCat

Item {
    id: root

    property bool active: false
    property string text: qsTr("Vibing mode")
    property color textColor: "#FFFFFF"
    property color catColor: "#FFFFFF"
    property color catOutlineColor: "#17152F"
    property color catShadeColor: "#CAD3DC"
    property color catCheekColor: "#F0A9B5"
    property color trailColor: "#FFFFFF"
    property real catAnimationSpeed: 1.0
    property int trailDotCount: 7
    property real trailLength: 44
    property real catTextGap: 7
    property real pixelsPerSecond: 126
    property real verticalPadding: 4
    property real horizontalPadding: 2

    property real travelProgress: 0.0
    property real trailPhase: 0.0

    readonly property real travelDistance:
        Math.max(1, root.width + runner.width)
    readonly property real effectivePixelsPerSecond:
        Math.max(1, root.pixelsPerSecond)
    readonly property int travelDuration:
        Math.max(
            1,
            Math.round(
                root.travelDistance
                / root.effectivePixelsPerSecond
                * 1000
            )
        )

    /*
     * The marquee no longer assumes a fixed compact height. Its natural height
     * is owned by the cat, with only enough padding for the walking bob.
     */
    implicitHeight: walkingCat.implicitHeight + 2 * verticalPadding
    implicitWidth: runnerWidth + 2 * horizontalPadding

    readonly property real runnerWidth:
        trailLength + walkingCat.width + catTextGap + marqueeLabel.implicitWidth

    clip: true

    Accessible.role: Accessible.StaticText
    Accessible.name: root.text

    function restartAnimations() {
        travelProgress = 0.0
        trailPhase = 0.0
        travelAnimation.restart()
        trailAnimation.restart()
    }

    function stopAnimations() {
        travelAnimation.stop()
        trailAnimation.stop()
        travelProgress = 0.0
        trailPhase = 0.0
    }

    function advanceTravel(frameTime) {
        if (!root.active || frameTime <= 0)
            return

        const distanceAdvanced =
            root.effectivePixelsPerSecond * frameTime
        const progressAdvanced =
            distanceAdvanced / root.travelDistance
        const nextProgress = root.travelProgress + progressAdvanced
        root.travelProgress = nextProgress - Math.floor(nextProgress)
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
        height: root.height
        x: -width + root.travelProgress * (root.width + width)

        Repeater {
            model: root.trailDotCount

            delegate: Rectangle {
                required property int index

                readonly property real age:
                    (root.trailPhase + index / root.trailDotCount) % 1.0
                readonly property real sizeFactor: 1.0 - age
                readonly property real catCenterY:
                    walkingCat.y + walkingCat.height * 0.56

                x: root.trailLength - 4 - age * root.trailLength - 10
                y: Math.round(
                       catCenterY
                       + ((index % 3) - 1) * 3
                       - height / 2
                   )
                width: Math.max(1, Math.round(5 * sizeFactor))
                height: width
                opacity: sizeFactor * sizeFactor
                color: root.trailColor
                radius: 0
            }
        }

        LongBarCat.SimpleWalkingCat {
            id: walkingCat

            x: root.trailLength
            y: Math.round((runner.height - height) / 2)
            running: root.active
            fillColor: root.catColor
            outlineColor: root.catOutlineColor
            shadeColor: root.catShadeColor
            cheekColor: root.catCheekColor
            animationSpeed: root.catAnimationSpeed
        }

        Label {
            id: marqueeLabel

            x: walkingCat.x + walkingCat.width + root.catTextGap
            anchors.verticalCenter: walkingCat.verticalCenter
            text: root.text
            color: root.textColor
            font.pixelSize: 14
            font.weight: Font.DemiBold
            font.letterSpacing: 0.8
            verticalAlignment: Text.AlignVCenter
        }
    }

    FrameAnimation {
        id: travelAnimation

        objectName: "marqueeTravelAnimation"
        onTriggered: root.advanceTravel(frameTime)
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
}
