import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: page
    objectName: "readingPage"
    property var s: controller.strings
    required property var controller
    required property var theme
    clip: true
    contentWidth: availableWidth

    Dialog {
        id: chapterConfirmation
        objectName: "chapterConfirmation"
        property int chapterIndex: -1
        property string chapterTitle: ""
        title: s["reading.inferred_confirm"]
        modal: true
        anchors.centerIn: parent
        width: Math.min(420, page.width - 32)
        standardButtons: Dialog.NoButton
        ColumnLayout {
            width: parent.width
            Label {
                text: chapterConfirmation.chapterTitle + "\n\n" + s["reading.inferred_hint"]
                textFormat: Text.PlainText
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }
            RowLayout {
                Button { text: s["reading.inferred_cancel"]; onClicked: chapterConfirmation.reject() }
                Button { text: s["reading.inferred_jump"]; onClicked: chapterConfirmation.accept() }
            }
        }
        onAccepted: controller.jumpToChapter(chapterIndex)
        onClosed: chapterPicker.currentIndex = Qt.binding(function() { return controller.currentChapter })
    }

    ColumnLayout {
        width: page.availableWidth
        spacing: 10
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
        Label { objectName: "section_book"; text: s["reading.section_book"]; font { pixelSize: 16; bold: true } color: page.theme.textPrimary; Layout.leftMargin: 28; Layout.topMargin: 16 }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            text: controller.title + "  \u00b7  " + controller.position + " / " + controller.groupCount
            color: page.theme.textPrimary
            wrapMode: Text.Wrap
            font { pixelSize: 18; bold: true }
        }
        RowLayout {
            Layout.leftMargin: 28
            Button {
                id: importButton
                background: Rectangle {
                    radius: 8
                    color: importButton.down ? page.theme.bgSubtle : page.theme.bgCard
                    border.color: page.theme.border || page.theme.textSecondary
                }
                text: controller.busy ? s["reading.importing"] : s["reading.import"]
                enabled: !controller.busy
                onClicked: controller.chooseDocument()
            }
        }
        RowLayout {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            Label { text: s["reading.chapters"]; color: page.theme.textPrimary }
            ComboBox {
                id: chapterPicker
                objectName: "readingChapterPicker"
                Layout.fillWidth: true
                model: controller.chapterLabels
                textRole: "label"
                currentIndex: controller.currentChapter
                enabled: count > 0 && !controller.busy
                displayText: currentIndex < 0 ? s["reading.choose_chapter"] : currentText
                onActivated: {
                    var entry = controller.chapters[currentIndex]
                    if (entry.inferred) {
                        chapterConfirmation.chapterIndex = currentIndex
                        chapterConfirmation.chapterTitle = entry.title
                        chapterConfirmation.open()
                    } else {
                        controller.jumpToChapter(currentIndex)
                    }
                }
                Accessible.name: s["reading.chapters"]
            }
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            text: controller.chaptersEstimated ? s["reading.chapters_estimated"] : s["reading.chapters_empty"]
            visible: controller.groupCount > 0 && (controller.chaptersEstimated || controller.chapters.length === 0)
            wrapMode: Text.Wrap
            color: page.theme.textSecondary
        }
        RowLayout {
            objectName: "section_reading"
            Layout.leftMargin: 28; Layout.rightMargin: 28; Layout.topMargin: 16
            spacing: 8
            Label { text: s["reading.section_reading"]; font { pixelSize: 16; bold: true } color: page.theme.textPrimary }
            ToolButton {
                id: readingHelp; objectName: "readingHelp"
                text: "?"; checkable: true
                implicitWidth: 28; implicitHeight: 28
                Accessible.name: s["reading.section_reading"] + " — " + s["reading.help"]
                ToolTip.visible: hovered
                ToolTip.text: s["reading.help"]
            }
        }
        Label {
                objectName: "readingHelpText"
                visible: readingHelp.checked
                Layout.leftMargin: 28; Layout.rightMargin: 28
                Layout.fillWidth: true; wrapMode: Text.Wrap
                color: page.theme.textSecondary
                text: s["reading.auto_hint"] + "\n\n" + s["reading.wheel_hint"]
            }
        RowLayout {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            Label { text: s["reading.enabled"]; color: page.theme.textPrimary; Layout.fillWidth: true }
            Switch {
                Accessible.name: s["reading.enabled"]
                checked: controller.enabled
                enabled: controller.supported && controller.groupCount > 0
                onToggled: controller.setEnabled(checked)
            }
        }
        RowLayout {
            Layout.leftMargin: 28
            Button {
                text: controller.autoRunning ? s["reading.auto_pause"] : s["reading.auto_start"]
                enabled: controller.enabled && controller.groupCount > 0
                onClicked: controller.setAutoRunning(!controller.autoRunning)
            }
            Label { text: s["reading.auto_speed"]; color: page.theme.textSecondary }
            Slider {
                from: 5; to: 100; stepSize: 1
                value: controller.scrollSpeed
                onMoved: controller.setScrollSpeed(Math.round(value))
                Accessible.name: s["reading.auto_speed"]
            }
            Label { text: controller.scrollSpeed + " " + s["reading.pixels_second"]; color: page.theme.textSecondary }
        }
        Rectangle {
            objectName: "readingPreview"
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
        }
        Label {
            Layout.leftMargin: 28
            Layout.rightMargin: 28
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            visible: !controller.supported
            text: s["reading.unsupported"]
            color: page.theme.textSecondary
        }
        RowLayout {
            objectName: "section_appearance"
            Layout.leftMargin: 28; Layout.rightMargin: 28; Layout.topMargin: 16
            spacing: 8
            Label { text: s["reading.section_appearance"]; font { pixelSize: 16; bold: true } color: page.theme.textPrimary }
            ToolButton {
                id: appearanceHelp; objectName: "appearanceHelp"
                text: "?"; checkable: true
                implicitWidth: 28; implicitHeight: 28
                Accessible.name: s["reading.section_appearance"] + " — " + s["reading.help"]
                ToolTip.visible: hovered
                ToolTip.text: s["reading.help"]
            }
        }
        Label {
                objectName: "appearanceHelpText"
                visible: appearanceHelp.checked
                Layout.leftMargin: 28; Layout.rightMargin: 28
                Layout.fillWidth: true; wrapMode: Text.Wrap
                color: page.theme.textSecondary
                text: s["reading.style_hint"]
            }
        GridLayout {
            columns: 6
            columnSpacing: 12; rowSpacing: 12
            Layout.leftMargin: 28; Layout.rightMargin: 28
            Layout.fillWidth: true
            Label { text: s["reading.mode"]; color: page.theme.textSecondary }
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
                Layout.columnSpan: 3
                Layout.fillWidth: true
                Accessible.name: s["reading.opacity"]
            }
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
                Layout.columnSpan: 2
                text: s["reading.auto_height"]
                checked: controller.panelHeight === 0
                onClicked: controller.setPanelHeight(checked ? 0 : 160)
            }
            CheckBox {
                Layout.columnSpan: 2
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
        RowLayout {
            objectName: "section_controls"
            Layout.leftMargin: 28; Layout.rightMargin: 28; Layout.topMargin: 16
            spacing: 8
            Label { text: s["reading.section_controls"]; font { pixelSize: 16; bold: true } color: page.theme.textPrimary }
            ToolButton {
                id: controlsHelp; objectName: "controlsHelp"
                text: "?"; checkable: true
                implicitWidth: 28; implicitHeight: 28
                Accessible.name: s["reading.section_controls"] + " — " + s["reading.help"]
                ToolTip.visible: hovered
                ToolTip.text: s["reading.help"]
            }
        }
        Label {
                objectName: "controlsHelpText"
                visible: controlsHelp.checked
                Layout.leftMargin: 28; Layout.rightMargin: 28
                Layout.fillWidth: true; wrapMode: Text.Wrap
                color: page.theme.textSecondary
                text: s["reading.hide_hint"]
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
            text: s["reading.hide_short"]
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
