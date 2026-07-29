pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Item {
    id: root

    required property var theme
    required property real marqueePixelsPerSecond

    default property alias contentData: contentHost.data

    property bool expanded: true
    property string panelTitle: qsTr("CONTROLS")
    property string marqueeText: qsTr("Vibing mode")
    property int headerHeight: 28
    property int contentPadding: 10
    property int collapsedPadding: 5

    /*
     * This remains externally overridable, but its default is now derived from
     * the marquee rather than fixed at 38 pixels.
     */
    property real collapsedBodyHeight:
        marquee.implicitHeight + 2 * collapsedPadding

    readonly property real expandedChromeHeight:
        headerHeight + 2 * contentPadding
    readonly property real expandedImplicitHeight:
        expandedChromeHeight + contentHost.implicitHeight
    readonly property real collapsedImplicitHeight:
        headerHeight + collapsedBodyHeight

    implicitHeight: expanded ? expandedImplicitHeight : collapsedImplicitHeight
    clip: true

    Accessible.role: Accessible.Pane
    Accessible.name: expanded
                     ? qsTr("Expanded visualizer controls")
                     : qsTr("Collapsed visualizer controls")

    onExpandedChanged: {
        if (!expanded)
            toggleButton.forceActiveFocus(Qt.OtherFocusReason)
    }

    Behavior on implicitHeight {
        NumberAnimation {
            duration: Math.max(160, root.theme.transitionDuration)
            easing.type: Easing.OutCubic
        }
    }

    Rectangle {
        anchors.fill: parent
        color: root.theme.elevatedOverlay
        border.color: root.theme.subtleBorder
        border.width: 1
        radius: root.theme.controlRadius
    }

    Button {
        id: toggleButton

        objectName: "controlsToggleButton"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: root.headerHeight
        activeFocusOnTab: true
        Accessible.name: root.expanded
                         ? qsTr("Collapse visualizer controls")
                         : qsTr("Expand visualizer controls")
        onClicked: root.expanded = !root.expanded

        contentItem: RowLayout {
            spacing: 8

            Label {
                Layout.fillWidth: true
                text: root.panelTitle
                color: root.theme.mutedText
                font.pixelSize: 10
                font.weight: Font.DemiBold
                font.letterSpacing: 1.2
                verticalAlignment: Text.AlignVCenter
            }

            Label {
                text: root.expanded ? "\u2303" : "\u2304"
                color: toggleButton.visualFocus
                       ? root.theme.accent
                       : root.theme.secondaryText
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        background: Rectangle {
            color: toggleButton.down ? root.theme.pressedOverlay
                                     : toggleButton.hovered ? root.theme.hoverOverlay
                                                            : "transparent"
            border.color: toggleButton.visualFocus
                          ? root.theme.accent
                          : "transparent"
            border.width: toggleButton.visualFocus ? 1 : 0
            radius: root.theme.controlRadius

            Behavior on color {
                ColorAnimation { duration: root.theme.transitionDuration }
            }
        }
    }

    Item {
        id: expandedViewport

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: toggleButton.bottom
        anchors.bottom: parent.bottom
        visible: root.expanded || opacity > 0.001
        enabled: root.expanded
        opacity: root.expanded ? 1.0 : 0.0
        clip: true

        Behavior on opacity {
            NumberAnimation {
                duration: Math.max(110, root.theme.transitionDuration)
                easing.type: Easing.OutCubic
            }
        }

        ColumnLayout {
            id: contentHost

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: root.contentPadding
            spacing: 0
        }
    }

    Item {
        id: collapsedViewport

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: toggleButton.bottom
        anchors.bottom: parent.bottom
        anchors.leftMargin: root.collapsedPadding
        anchors.rightMargin: root.collapsedPadding
        anchors.topMargin: root.collapsedPadding
        anchors.bottomMargin: root.collapsedPadding
        visible: !root.expanded || opacity > 0.001
        enabled: !root.expanded
        opacity: root.expanded ? 0.0 : 1.0
        clip: true

        Behavior on opacity {
            NumberAnimation {
                duration: Math.max(110, root.theme.transitionDuration)
                easing.type: Easing.OutCubic
            }
        }

        VibingMarquee {
            id: marquee

            objectName: "vibingMarquee"
            anchors.fill: parent
            active: !root.expanded && collapsedViewport.visible
            text: root.marqueeText
            pixelsPerSecond: root.marqueePixelsPerSecond
            textColor: root.theme.primaryText
            catColor: "#FFFFFF"
            trailColor: "#FFFFFF"
        }
    }
}
