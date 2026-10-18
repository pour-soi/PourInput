import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

Button {
    id: control
    readonly property var theme: Theme.palette(uiState.darkMode)
    property bool destructive: false
    implicitHeight: 42
    implicitWidth: Math.max(42, implicitContentWidth + 28)
    leftPadding: 12; rightPadding: 12
    topPadding: 8; bottomPadding: 8
    topInset: 0; bottomInset: 0
    font { family: uiState.fontFamily; pixelSize: 16 }
    contentItem: Text {
        text: control.text
        font: control.font
        color: control.destructive ? control.theme.danger : control.theme.textPrimary
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        opacity: control.enabled ? 1 : 0.45
    }
    background: Rectangle {
        radius: Theme.radiusSmall
        color: control.destructive ? (control.hovered || control.down ? control.theme.dangerBg : "transparent")
             : control.down ? control.theme.accentDim
             : control.hovered ? control.theme.bgCardHover : control.theme.bgCard
        border.color: control.activeFocus ? control.theme.accent
                    : control.destructive ? "transparent" : control.theme.border
        opacity: control.enabled ? 1 : 0.55
    }
}
