import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: page
    property var s: controller.strings
    required property var controller
    required property var theme
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: page.availableWidth
        spacing: 18
        Item { Layout.preferredHeight: 12 }
        Label {
            text: s["reading.title"]
            font.pixelSize: 28
            color: page.theme.textPrimary
            Layout.leftMargin: 28
        }
        Label {
            text: s["reading.subtitle"]
            color: page.theme.textSecondary
            Layout.leftMargin: 28
        }
        RowLayout {
            Layout.leftMargin: 28
            Button {
                text: controller.busy ? s["reading.importing"] : s["reading.import"]
                enabled: !controller.busy
                onClicked: controller.chooseDocument()
            }
            Switch {
                text: s["reading.enabled"]
                checked: controller.enabled
                enabled: controller.supported && controller.groupCount > 0
                onToggled: controller.setEnabled(checked)
            }
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            text: controller.title + "  ·  " + controller.position + " / " + controller.groupCount
            color: page.theme.textPrimary
            elide: Text.ElideMiddle
        }
        Rectangle {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            implicitHeight: preview.implicitHeight + 32
            radius: 10
            color: page.theme.bgCard
            Label {
                id: preview
                anchors.fill: parent
                anchors.margins: 16
                text: controller.text || s["reading.empty"]
                textFormat: Text.PlainText
                wrapMode: Text.Wrap
                color: page.theme.textPrimary
                font.pixelSize: 18
            }
        }
        RowLayout {
            Layout.leftMargin: 28
            Button { text: s["reading.previous"]; enabled: controller.enabled && controller.position > 1; onClicked: controller.move(-1) }
            Button { text: s["reading.next"]; enabled: controller.enabled && controller.position < controller.groupCount; onClicked: controller.move(1) }
            ComboBox {
                model: [s["reading.normal"], s["reading.minimal"], s["reading.ghost"]]
                currentIndex: ["Normal", "Minimal", "Ghost"].indexOf(controller.displayMode)
                onActivated: controller.setDisplayMode(["Normal", "Minimal", "Ghost"][currentIndex])
                Accessible.name: s["reading.mode"]
            }
            Label { text: s["reading.opacity"]; color: page.theme.textSecondary }
            Slider {
                from: 0.2; to: 1; value: controller.panelOpacity
                onPressedChanged: if (!pressed) controller.setOpacity(value)
                Accessible.name: s["reading.opacity"]
            }
        }
        RowLayout {
            Layout.leftMargin: 28
            Label { text: s["reading.width"]; color: page.theme.textSecondary }
            SpinBox {
                from: 240; to: 1920; stepSize: 20
                editable: true
                value: controller.panelWidth
                onValueModified: controller.setPanelWidth(value)
                Accessible.name: s["reading.width"]
            }
            Label { text: s["reading.height"]; color: page.theme.textSecondary }
            SpinBox {
                from: 80; to: 1080; stepSize: 20
                editable: true
                enabled: controller.panelHeight !== 0
                value: controller.panelHeight || 160
                onValueModified: controller.setPanelHeight(value)
                Accessible.name: s["reading.height"]
            }
            CheckBox {
                text: s["reading.auto_height"]
                checked: controller.panelHeight === 0
                onClicked: controller.setPanelHeight(checked ? 0 : 160)
            }
        }
        RowLayout {
            Layout.leftMargin: 28
            CheckBox {
                text: s["reading.transparent"]
                checked: controller.transparentBackground
                onClicked: controller.setTransparentBackground(checked)
            }
            Label { text: s["reading.font_size"]; color: page.theme.textSecondary }
            SpinBox {
                from: 12; to: 72
                editable: true
                value: controller.fontSize || (controller.displayMode === "Normal" ? 22 : 19)
                onValueModified: controller.setFontSize(value)
                Accessible.name: s["reading.font_size"]
            }
            Button { text: s["reading.font_color"]; onClicked: controller.chooseFontColor() }
            TextField {
                Layout.preferredWidth: 112
                text: controller.fontColor
                validator: RegularExpressionValidator { regularExpression: /#[0-9a-fA-F]{6}/ }
                onEditingFinished: {
                    if (acceptableInput) controller.setFontColor(text)
                    text = Qt.binding(function() { return controller.fontColor })
                }
                Accessible.name: s["reading.hex"]
            }
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            text: s["reading.style_hint"]
            wrapMode: Text.Wrap
            color: page.theme.textSecondary
        }
        RowLayout {
            Layout.leftMargin: 28
            Label { text: s["reading.hide"]; color: page.theme.textSecondary }
            ComboBox {
                model: controller.hideChoices
                textRole: "label"
                valueRole: "key"
                Layout.preferredWidth: 200
                currentIndex: {
                    var choices = controller.hideChoices
                    for (var i = 0; i < choices.length; ++i) {
                        if (choices[i].key === controller.hideKey)
                            return i
                    }
                    return 0
                }
                onActivated: controller.setHideKey(currentValue)
                Accessible.name: s["reading.hide_choice"]
            }
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            text: s["reading.hide_hint"]
            color: page.theme.textSecondary
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            text: controller.supported
                  ? s["reading.wheel_hint"]
                  : s["reading.unsupported"]
            color: page.theme.textSecondary
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            visible: controller.error.length > 0
            text: controller.error
            wrapMode: Text.Wrap
            color: "#d36c63"
        }
        Item { Layout.preferredHeight: 24 }
    }
}

