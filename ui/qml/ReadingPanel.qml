import QtQuick
import QtQuick.Window

Window {
    id: panel
    required property var controller
    readonly property bool normal: controller.displayMode === "Normal"
    flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
           | Qt.WindowDoesNotAcceptFocus
           | (normal ? 0 : Qt.WindowTransparentForInput)
    visible: controller.panelVisible
    color: "transparent"
    opacity: controller.panelOpacity * (controller.displayMode === "Ghost" ? 0.55 : 1)
    width: Math.min(controller.panelWidth, Screen.width - 40)
    readonly property real verticalPadding: normal ? 40 + heading.height + content.spacing : 24
    height: Math.min(Math.max(controller.panelHeight || 240, controller.readerLineHeight + verticalPadding),
                     Screen.height - 140)
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + Screen.height - height - 100
    title: controller.strings["reading.panel_title"]
    transientParent: null

    Rectangle {
        anchors.fill: parent
        radius: panel.normal ? 14 : 6
        objectName: "readingBackground"
        color: controller.transparentBackground ? "transparent"
               : (controller.displayMode === "Ghost" ? "#9018202a" : "#f018202a")
        Column {
            id: content
            anchors.centerIn: parent
            width: parent.width - (panel.normal ? 40 : 24)
            spacing: 10
            Text {
                id: heading
                visible: panel.normal
                width: parent.width
                text: controller.title + "  ·  " + controller.position + " / " + controller.groupCount
                color: controller.fontColor
                opacity: 0.7
                font.pixelSize: 12
                elide: Text.ElideRight
            }
            Item {
                width: parent.width
                height: Math.max(1, panel.height - panel.verticalPadding)
                clip: true
                Text {
                    id: body
                    width: parent.width
                    text: controller.text
                    textFormat: Text.PlainText
                    wrapMode: Text.Wrap
                    objectName: "readingBody"
                    color: controller.fontColor
                    font.pixelSize: controller.fontSize || (panel.normal ? 22 : 19)
                    y: -controller.scrollOffset
                    height: parent.height + (controller.continuousScroll ? controller.readerLineHeight * 2 : 0)
                    clip: true
                    fontSizeMode: Text.FixedSize
                    renderType: Text.QtRendering
                    lineHeightMode: Text.FixedHeight
                    lineHeight: controller.readerLineHeight
                    function updateViewport() { controller.setViewport(width, parent.height, font) }
                    onWidthChanged: Qt.callLater(updateViewport)
                    onHeightChanged: Qt.callLater(updateViewport)
                    onFontChanged: Qt.callLater(updateViewport)
                    Component.onCompleted: Qt.callLater(updateViewport)
                }
            }
        }
        MouseArea {
            enabled: panel.normal
            anchors.fill: parent
            onPressed: panel.startSystemMove()
        }
    }

    // Separate input surface keeps Minimal/Ghost text click-through.
    Window {
        id: dragHandle
        objectName: "readingDragHandle"
        transientParent: null
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
        visible: panel.visible
        color: "transparent"
        width: 40; height: 40
        x: panel.x + panel.width - width
        y: panel.y - height - 8
        title: controller.strings["reading.move"]
        Item {
            anchors.fill: parent
            Image {
                objectName: "readingMoveIcon"
                anchors.centerIn: parent
                width: 38; height: 38
                source: "assets/reading-move.png"
                sourceSize.width: 152
                sourceSize.height: 152
                fillMode: Image.PreserveAspectFit
                smooth: true
            }
            MouseArea {
                id: grip
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.SizeAllCursor
                property point startPointer
                property point startPanel
                Accessible.name: controller.strings["reading.move"]
                onPressed: function(mouse) {
                    startPointer = mapToGlobal(mouse.x, mouse.y)
                    startPanel = Qt.point(panel.x, panel.y)
                }
                onPositionChanged: function(mouse) {
                    if (!pressed) return
                    var point = mapToGlobal(mouse.x, mouse.y)
                    panel.x = startPanel.x + point.x - startPointer.x
                    panel.y = startPanel.y + point.y - startPointer.y
                }
            }
        }
    }

    Window {
        id: resizeHandle
        objectName: "readingResizeHandle"
        transientParent: null
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
        visible: panel.visible
        color: "transparent"
        width: 24; height: 24
        x: panel.x + panel.width - width
        y: panel.y + panel.height - height
        title: controller.strings["reading.resize"]
        Item {
            anchors.fill: parent
            Text {
                anchors.centerIn: parent
                text: "⌟"
                color: controller.fontColor
                font.pixelSize: 16
                opacity: resizeGrip.containsMouse || resizeGrip.pressed ? 0.85 : 0.18
            }
            MouseArea {
                id: resizeGrip
                objectName: "readingResizeGrip"
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.SizeFDiagCursor
                property point startPointer
                property size startSize
                Accessible.name: controller.strings["reading.resize"]
                onPressed: function(mouse) {
                    startPointer = mapToGlobal(mouse.x, mouse.y)
                    startSize = Qt.size(panel.width, panel.height)
                    // Keep the top-left stationary while the bottom-right moves.
                    panel.x = panel.x
                    panel.y = panel.y
                }
                onPositionChanged: function(mouse) {
                    if (!pressed) return
                    var point = mapToGlobal(mouse.x, mouse.y)
                    panel.width = Math.max(240, Math.min(1920, Screen.width - 40,
                        startSize.width + point.x - startPointer.x))
                    panel.height = Math.max(80, Math.min(1080, Screen.height - 140,
                        startSize.height + point.y - startPointer.y))
                }
                function saveSize() {
                    controller.setPanelSize(Math.round(panel.width), Math.round(panel.height))
                    panel.width = Qt.binding(function() { return Math.min(controller.panelWidth, Screen.width - 40) })
                    panel.height = Qt.binding(function() {
                        return Math.min(Math.max(controller.panelHeight || 240, controller.readerLineHeight + panel.verticalPadding), Screen.height - 140)
                    })
                }
                onReleased: saveSize()
                onCanceled: saveSize()
            }
        }
    }
}
