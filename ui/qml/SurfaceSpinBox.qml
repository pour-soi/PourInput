import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

SpinBox {
    id: control
    readonly property var theme: Theme.palette(uiState.darkMode)
    implicitWidth: 160
    implicitHeight: 42
    leftPadding: 42; rightPadding: 42
    topInset: 0; bottomInset: 0
    font { family: uiState.fontFamily; pixelSize: 16 }
    contentItem: TextInput {
        text: control.textFromValue(control.value, control.locale)
        font: control.font
        color: control.theme.textPrimary
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        readOnly: !control.editable
        validator: control.validator
        inputMethodHints: control.inputMethodHints
        opacity: control.enabled ? 1 : 0.45
    }
    up.indicator: Rectangle {
        x: control.width - width
        width: 38; height: control.height; radius: 8
        color: control.up.pressed ? control.theme.accentDim : control.up.hovered ? control.theme.bgCardHover : "transparent"
        Text { anchors.centerIn: parent; text: "+"; font: control.font; color: control.theme.textSecondary; opacity: control.up.enabled ? 1 : 0.45 }
    }
    down.indicator: Rectangle {
        width: 38; height: control.height; radius: 8
        color: control.down.pressed ? control.theme.accentDim : control.down.hovered ? control.theme.bgCardHover : "transparent"
        Text { anchors.centerIn: parent; text: "−"; font: control.font; color: control.theme.textSecondary; opacity: control.down.enabled ? 1 : 0.45 }
    }
    background: Rectangle {
        radius: 8
        color: control.theme.bgCard
        border.color: control.activeFocus ? control.theme.accent : control.theme.border
        opacity: control.enabled ? 1 : 0.55
    }
}
