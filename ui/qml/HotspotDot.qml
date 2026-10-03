import QtQuick
import "Theme.js" as Theme

/*  A single clickable hotspot dot placed over the mouse image.
    Position is given as normalised coordinates (0-1) within the
    source image, so it adapts when the image is scaled.

    MousePage assigns non-overlapping annotation columns; connecting
    lines track their measured positions.                                    */

Item {
    id: hotspot
    objectName: "hotspot_" + buttonKey
    readonly property var theme: Theme.palette(uiState.darkMode)

    // ── Required properties ───────────────────────────────────
    required property var imgItem         // the Image element
    required property real normX          // 0-1 x in source image
    required property real normY          // 0-1 y in source image
    required property string buttonKey    // config key (e.g. "middle")
    property bool isHScroll: false        // true for horizontal scroll dot

    property string label: ""
    property string sublabel: ""
    property string labelSide: "right"    // "left" or "right"

    // ── Computed centre ───────────────────────────────────────
    property real cx: imgItem.x + imgItem.offX + normX * imgItem.paintedWidth
    property real cy: imgItem.y + imgItem.offY + normY * imgItem.paintedHeight

    property bool isSelected: isHScroll ? mousePage.selectedButton === "hscroll_left"
                                        : mousePage.selectedButton === buttonKey
    property bool configured: true
    property bool isHovered: dotMa.containsMouse
    property real labelWidth: 220
    property real labelHeight: labelCol.implicitHeight + 14
    property real labelX: 16
    property real labelY: 20
    property real labelCenterX: labelX + labelWidth / 2
    property bool sourceIsRightOfLabel: cx >= labelCenterX
    property real lineEndX: sourceIsRightOfLabel
                            ? labelX + labelWidth - 6
                            : labelX + 6
    property real lineEndY: labelY + labelHeight / 2
    // Leave the image horizontally, then fan out only in the exterior gutter.
    property real lineBendX: labelSide === "left" ? imgItem.x - 8 : imgItem.x + imgItem.width + 8
    property real connectorOpacity: isSelected ? 0.8 : mousePage.selectedButton !== "" ? 0.12 : 0.23


    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: label

    function triggerSelection() {
        if (isHScroll)
            mousePage.selectHScroll()
        else
            mousePage.selectButton(buttonKey)
    }

    Keys.onReturnPressed: triggerSelection()
    Keys.onEnterPressed: triggerSelection()
    Keys.onSpacePressed: triggerSelection()

    // ── Glow ring ─────────────────────────────────────────────
    Rectangle {
        id: glow
        x: cx - width / 2
        y: cy - height / 2
        width: 30; height: 30; radius: 15
        color: "transparent"
        border.width: isSelected || hotspot.activeFocus ? 2 : 1
        border.color: isSelected || hotspot.activeFocus
                      ? theme.accent
                      : Qt.rgba(0.36, 0.56, 0.95, 0.3)
        opacity: isSelected || isHovered || hotspot.activeFocus ? 1 : 0.6

        Behavior on opacity { NumberAnimation { duration: 200 } }
        Behavior on border.width { NumberAnimation { duration: 150 } }

        // Pulse animation when selected
        SequentialAnimation on scale {
            loops: Animation.Infinite
            running: isSelected
            NumberAnimation { from: 1.0; to: 1.25; duration: 800; easing.type: Easing.InOutQuad }
            NumberAnimation { from: 1.25; to: 1.0; duration: 800; easing.type: Easing.InOutQuad }
        }
    }

    // ── Dot ───────────────────────────────────────────────────
    Rectangle {
        id: dot
        x: cx - width / 2
        y: cy - height / 2
        width: 16; height: 16; radius: 8
        color: configured ? (isSelected ? theme.accentHover : theme.accent) : theme.bg
        border.width: 2
        border.color: hotspot.activeFocus ? theme.textPrimary : theme.accent

        scale: isHovered ? 1.2 : 1.0
        Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // ── Click area (larger than the dot for easier targeting) ─
    MouseArea {
        id: dotMa
        x: cx - 18
        y: cy - 18
        width: 36; height: 36
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: hotspot.triggerSelection()
    }

    // ── Connecting line ───────────────────────────────────────
    Canvas {
        id: lineCanvas
        anchors.fill: parent
        z: 0
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.strokeStyle = theme.accent
            ctx.globalAlpha = connectorOpacity
            ctx.lineWidth = 1
            ctx.setLineDash([])
            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(lineBendX, cy)
            ctx.lineTo(lineEndX, lineEndY)
            ctx.stroke()
        }

        // Repaint when position or selection changes
        Connections {
            target: hotspot
            function onCxChanged() { lineCanvas.requestPaint() }
            function onCyChanged() { lineCanvas.requestPaint() }
            function onIsSelectedChanged() { lineCanvas.requestPaint() }
            function onLabelXChanged() { lineCanvas.requestPaint() }
            function onLabelYChanged() { lineCanvas.requestPaint() }
            function onLineEndXChanged() { lineCanvas.requestPaint() }
            function onLineEndYChanged() { lineCanvas.requestPaint() }
            function onLineBendXChanged() { lineCanvas.requestPaint() }
            function onConnectorOpacityChanged() { lineCanvas.requestPaint() }
        }
        Component.onCompleted: requestPaint()
    }

    // ── Annotation label ──────────────────────────────────────
    Rectangle {
        id: labelBg
        z: 2
        x: labelX
        y: labelY
        width: labelWidth
        height: labelHeight
        radius: 8
        color: isSelected
               ? (uiState.darkMode
                  ? Qt.rgba(0.36, 0.56, 0.95, 0.12)
                  : Qt.rgba(0.82, 0.97, 0.93, 0.9))
                          : uiState.darkMode ? Qt.rgba(0, 0, 0, 0.35) : Qt.rgba(1, 1, 1, 0.92)
        border.width: isSelected || hotspot.activeFocus ? 1 : 0
        border.color: Qt.rgba(0.36, 0.56, 0.95, 0.3)

        Behavior on color { ColorAnimation { duration: 200 } }

        Column {
            id: labelCol
            anchors {
                left: parent.left; leftMargin: 10
                verticalCenter: parent.verticalCenter
            }
            width: parent.width - 20
            spacing: 4

            Text {
                // lm.strings read creates a binding dependency → auto-updates on language change
                text: { var _lang = lm.strings; return lm.trButton(hotspot.label) }
                width: parent.width
                wrapMode: Text.Wrap
                font { family: uiState.fontFamily; pixelSize: 15; bold: true }
                color: isSelected ? theme.accent : theme.textPrimary
            }

            Text {
                text: { var _lang = lm.strings; return lm.trAction(hotspot.sublabel) }
                font { family: uiState.fontFamily; pixelSize: 13 }
                color: theme.textSecondary
                visible: hotspot.sublabel !== ""
                width: parent.width
                wrapMode: Text.Wrap
            }
        }

        // Make label clickable too
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: hotspot.triggerSelection()
        }
    }

    // ── Small dot at the end of the line ──────────────────────
    Rectangle {
        z: 1
        x: lineEndX - 3
        y: lineEndY - 3
        width: 6; height: 6; radius: 3
        color: theme.accent
        opacity: connectorOpacity
    }
}
