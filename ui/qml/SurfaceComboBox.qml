import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

ComboBox {
    id: control
    readonly property var theme: Theme.palette(uiState.darkMode)
    implicitHeight: 42
    leftPadding: 14; rightPadding: 34
    topInset: 0; bottomInset: 0
    font { family: uiState.fontFamily; pixelSize: 16 }
    contentItem: Text {
        text: control.displayText
        font: control.font
        color: control.theme.textPrimary
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    indicator: Text {
        x: control.width - width - 14
        y: (control.height - height) / 2
        text: "\u2304"
        color: control.theme.textSecondary
        font { family: uiState.fontFamily; pixelSize: 16 }
    }
    background: Rectangle {
        radius: Theme.radiusSmall
        color: control.down ? control.theme.accentDim
             : control.hovered ? control.theme.bgCardHover : control.theme.bgCard
        border.color: control.activeFocus ? control.theme.accent : control.theme.border
    }
}
