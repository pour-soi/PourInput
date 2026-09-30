import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

Column {
    id: selector
    readonly property var theme: Theme.palette(uiState.darkMode)
    property var categories: backend.actionCategories
    property string currentAction: "none"
    property string editorKey: ""
    property var expanded: ({})
    signal picked(string aid)
    spacing: 6

    function selectedCategory() {
        if (currentAction.indexOf("custom:") === 0) return "Custom"
        for (var i = 0; i < categories.length; ++i)
            for (var j = 0; j < categories[i].actions.length; ++j)
                if (categories[i].actions[j].id === currentAction) return categories[i].category
        return "Other"
    }
    function openSelected(reset) {
        var next = reset ? ({}) : Object.assign({}, expanded)
        next[selectedCategory()] = true
        expanded = next
    }
    function toggleCategory(category) {
        var next = Object.assign({}, expanded)
        next[category] = !next[category]
        expanded = next
    }
    onEditorKeyChanged: Qt.callLater(function() { openSelected(true) })
    onCurrentActionChanged: openSelected(false)
    onCategoriesChanged: openSelected(false)
    onVisibleChanged: if (visible) openSelected(true)
    Component.onCompleted: openSelected(true)

    Flow {
        width: parent.width
        spacing: 10
        bottomPadding: 6
        Text {
            text: lm.strings["mouse.current_action"]
            font { family: uiState.fontFamily; pixelSize: 12 }
            color: theme.textDim
        }
        Text {
            width: Math.min(implicitWidth, selector.width)
            text: { var language = lm.strings; return lm.trAction(backend.actionLabelFor(selector.currentAction)) }
            wrapMode: Text.Wrap
            font { family: uiState.fontFamily; pixelSize: 12 }
            color: theme.textSecondary
        }
    }
    Repeater {
        model: selector.categories
        delegate: Column {
            id: section
            required property var modelData
            width: selector.width
            spacing: 8
            Button {
                objectName: "category_" + section.modelData.category
                width: parent.width
                implicitHeight: 34
                checkable: true
                checked: selector.expanded[section.modelData.category] === true
                onClicked: selector.toggleCategory(section.modelData.category)
                contentItem: Text {
                    text: (parent.checked ? "−  " : "+  ") + (lm.strings, lm.trCategory(section.modelData.category))
                    color: theme.textPrimary
                    font { family: uiState.fontFamily; pixelSize: 12 }
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: Theme.radiusSmall
                    color: parent.hovered || parent.activeFocus ? theme.bgCardHover : "transparent"
                }
                Accessible.name: (lm.strings, lm.trCategory(section.modelData.category))
            }
            Flow {
                width: parent.width
                spacing: 8
                visible: selector.expanded[section.modelData.category] === true
                Repeater {
                    model: section.modelData.actions
                    delegate: ActionChip {
                        required property var modelData
                        objectName: "action_" + modelData.id
                        maximumWidth: selector.width
                        actionId: modelData.id
                        actionLabel: (lm.strings, lm.trAction(modelData.id === "__custom__" && selector.currentAction.indexOf("custom:") === 0
                                     ? backend.actionLabelFor(selector.currentAction) : modelData.label))
                        isCurrent: modelData.id === "__custom__" ? selector.currentAction.indexOf("custom:") === 0
                                                               : selector.currentAction === modelData.id
                        onPicked: function(aid) { selector.picked(aid) }
                    }
                }
            }
        }
    }
}
