import QtQuick
import "Theme.js" as Theme

/*  A single action chip for the action picker.  */

Rectangle {
    id: chip
    readonly property var theme: Theme.palette(uiState.darkMode)

    property string actionId: ""
    property string actionLabel: ""
    property bool isCurrent: false

    property real maximumWidth: 10000

    signal picked(string aid)

    width: Math.min(maximumWidth, chipText.implicitWidth + 24)
    height: Math.max(34, chipText.implicitHeight + 16)
    radius: 9
    activeFocusOnTab: true

    Accessible.role: Accessible.Button
    Accessible.name: actionLabel

    color: isCurrent
           ? theme.accent
           : chipMa.containsMouse
             ? theme.bgCardHover
             : theme.bgCard
    border.width: activeFocus ? 2 : 1
    border.color: isCurrent ? theme.accent : activeFocus ? theme.accent : theme.border

    Behavior on color { ColorAnimation { duration: 120 } }

    Keys.onReturnPressed: chip.picked(actionId)
    Keys.onEnterPressed: chip.picked(actionId)
    Keys.onSpacePressed: chip.picked(actionId)

    Text {
        id: chipText
        anchors.centerIn: parent
        width: parent.width - 24
        wrapMode: Text.Wrap
        text: actionLabel
        font { family: uiState.fontFamily; pixelSize: 15 }
        color: isCurrent ? theme.bgSidebar : theme.textPrimary
    }

    MouseArea {
        id: chipMa
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: chip.picked(actionId)
    }
}
