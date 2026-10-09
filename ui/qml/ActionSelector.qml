import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

Column {
    id: selector
    readonly property var theme: Theme.palette(uiState.darkMode)
    property var categories: backend.actionCategories
    property string currentAction: "none"
    property string editorKey: ""
    property bool showCurrentAction: true
    property string activeCategory: "Other"
    signal picked(string aid)
    spacing: 12

    function selectedCategory() {
        if (currentAction.indexOf("custom:") === 0) return "Custom"
        for (var i = 0; i < categories.length; ++i)
            for (var j = 0; j < categories[i].actions.length; ++j)
                if (categories[i].actions[j].id === currentAction) return categories[i].category
        return "Other"
    }
    function selectCurrentCategory() {
        activeCategory = selectedCategory()
    }
    onEditorKeyChanged: Qt.callLater(selectCurrentCategory)
    onCurrentActionChanged: selectCurrentCategory()
    onCategoriesChanged: selectCurrentCategory()
    onVisibleChanged: if (visible) selectCurrentCategory()
    Component.onCompleted: selectCurrentCategory()

    Flow {
        visible: selector.showCurrentAction
        width: parent.width
        spacing: 10
        bottomPadding: 6
        Text {
            text: lm.strings["mouse.current_action"]
            font { family: uiState.fontFamily; pixelSize: 15 }
            color: theme.textDim
        }
        Text {
            width: Math.min(implicitWidth, selector.width)
            text: { var language = lm.strings; return lm.trAction(backend.actionLabelFor(selector.currentAction)) }
            wrapMode: Text.Wrap
            font { family: uiState.fontFamily; pixelSize: 17 }
            color: theme.textSecondary
        }
    }
    Flow {
        width: parent.width
        spacing: 8
        Repeater {
            model: selector.categories
            delegate: Button {
                required property var modelData
                objectName: "category_" + modelData.category
                implicitHeight: 44
                topInset: 0; bottomInset: 0
                horizontalPadding: 14
                checkable: true
                autoExclusive: true
                checked: selector.activeCategory === modelData.category
                onClicked: selector.activeCategory = modelData.category
                contentItem: Text {
                    text: (lm.strings, lm.trCategory(parent.modelData.category))
                    color: parent.checked ? theme.accent : theme.textSecondary
                    font { family: uiState.fontFamily; pixelSize: 17; bold: parent.checked }
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: 8
                    color: parent.hovered ? theme.bgCardHover : "transparent"
                    border.color: parent.activeFocus ? theme.accent : "transparent"
                    Rectangle {
                        anchors.bottom: parent.bottom
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width - 20; height: 2
                        visible: parent.parent.checked
                        color: theme.accent
                    }
                }
                Accessible.name: (lm.strings, lm.trCategory(modelData.category))
            }
        }
    }
    Repeater {
        model: selector.categories
        delegate: Column {
            id: section
            required property var modelData
            width: selector.width
            spacing: 10
            visible: selector.activeCategory === modelData.category
            topPadding: 12
            Text {
                text: (lm.strings, lm.trCategory(section.modelData.category))
                font { family: uiState.fontFamily; pixelSize: 18; bold: true }
                color: theme.textSecondary
            }
            Flow {
                width: parent.width
                spacing: 10
                visible: selector.activeCategory === section.modelData.category
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
