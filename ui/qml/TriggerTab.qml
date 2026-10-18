import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

TabButton {
    id: control
    readonly property var theme: Theme.palette(uiState.darkMode)
    implicitHeight: 42
    leftPadding: 14; rightPadding: 14
    topInset: 0; bottomInset: 0
    font { family: uiState.fontFamily; pixelSize: 16 }
    contentItem: Text {
        text: control.text
        font: control.font
        color: control.checked ? control.theme.accent : control.theme.textSecondary
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: Theme.radiusSmall
        color: control.checked ? control.theme.accentDim
             : control.hovered ? control.theme.bgCardHover : "transparent"
        border.color: control.activeFocus ? control.theme.accent : "transparent"
    }
}
