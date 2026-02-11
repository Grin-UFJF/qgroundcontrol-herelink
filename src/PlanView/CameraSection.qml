import QtQuick          2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts  1.2

import QGroundControl                   1.0
import QGroundControl.ScreenTools       1.0
import QGroundControl.Controls          1.0
import QGroundControl.FactControls      1.0
import QGroundControl.Palette           1.0

// Camera section for mission item editors
Column {
    anchors.left:   parent.left
    anchors.right:  parent.right
    spacing:        _margin

    property alias exclusiveGroup:  cameraSectionHeader.exclusiveGroup
    property alias showSpacer:      cameraSectionHeader.showSpacer
    property alias checked:         cameraSectionHeader.checked

    property var    _camera:        missionItem.cameraSection
    property real   _fieldWidth:    ScreenTools.defaultFontPixelWidth * 16
    property real   _margin:        ScreenTools.defaultFontPixelWidth / 2



    SectionHeader {
        id:             cameraSectionHeader
        anchors.left:   parent.left
        anchors.right:  parent.right
        text:           qsTr("Camera")
        checked:        false
    }

    Column {
        anchors.left:   parent.left
        anchors.right:  parent.right
        spacing:        _margin
        visible:        cameraSectionHeader.checked

        FactComboBox {
            id:             cameraActionCombo
            anchors.left:   parent.left
            anchors.right:  parent.right
            fact:           _camera.cameraAction
            indexModel:     false
        }

        FactComboBox {
            id:             inspectionTypeCombo
            anchors.left:   parent.left
            anchors.right:  parent.right
            fact:           _camera.inspectionType
            indexModel:     false
            visible:        _camera.cameraAction.rawValue === 6 // Take Photo
        }

        ColumnLayout {
            anchors.left:   parent.left
            anchors.right:  parent.right
            spacing:        ScreenTools.defaultFontPixelWidth / 2
            visible:        _camera.cameraAction.rawValue === 6 // Take Photo

            QGCLabel {
                text:           qsTr("Zoom")
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: ScreenTools.defaultFontPixelWidth

                Slider {
                    Layout.fillWidth: true
                    minimumValue: 0
                    maximumValue: 100
                    value: _camera.zoomLevel ? _camera.zoomLevel.value : 0
                    onValueChanged: {
                        if (_camera.zoomLevel) {
                            _camera.zoomLevel.value = value
                        }
                    }
                }

                FactTextField {
                    fact:               _camera.zoomLevel
                    Layout.preferredWidth: ScreenTools.defaultFontPixelWidth * 6
                }
            }
        }

        RowLayout {
            anchors.left:   parent.left
            anchors.right:  parent.right
            spacing:        ScreenTools.defaultFontPixelWidth
            visible:        _camera.cameraAction.rawValue === 1

            QGCLabel {
                text:               qsTr("Time")
                Layout.fillWidth:   true
            }
            FactTextField {
                fact:                   _camera.cameraPhotoIntervalTime
                Layout.preferredWidth:  _fieldWidth
            }
        }

        RowLayout {
            anchors.left:   parent.left
            anchors.right:  parent.right
            spacing:        ScreenTools.defaultFontPixelWidth
            visible:        _camera.cameraAction.rawValue === 2

            QGCLabel {
                text:               qsTr("Distance")
                Layout.fillWidth:   true
            }
            FactTextField {
                fact:                   _camera.cameraPhotoIntervalDistance
                Layout.preferredWidth:  _fieldWidth
            }
        }

        RowLayout {
            anchors.left:   parent.left
            anchors.right:  parent.right
            spacing:        ScreenTools.defaultFontPixelWidth
            visible:        false

            QGCCheckBox {
                id:                 modeCheckBox
                text:               qsTr("Mode")
                checked:            _camera.specifyCameraMode
                onClicked:          _camera.specifyCameraMode = checked
            }
            FactComboBox {
                fact:               _camera.cameraMode
                indexModel:         false
                enabled:            modeCheckBox.checked
                Layout.fillWidth:   true
            }
        }

        ColumnLayout {
            anchors.left:   parent.left
            anchors.right:  parent.right
            spacing:        ScreenTools.defaultFontPixelWidth / 2

            QGCCheckBox {
                id:                 gimbalCheckBox
                text:               qsTr("Gimbal")
                checked:            _camera.specifyGimbal
                onClicked:          _camera.specifyGimbal = checked
            }

            QGCLabel {
                text:           qsTr("Pitch")
                visible:        gimbalCheckBox.checked
            }

            RowLayout {
                visible:            gimbalCheckBox.checked
                Layout.fillWidth:   true
                spacing:            ScreenTools.defaultFontPixelWidth

                Slider {
                    Layout.fillWidth: true
                    minimumValue: 0
                    maximumValue: 90
                    value: _camera.gimbalPitch.value
                    onValueChanged: _camera.gimbalPitch.value = value
                }

                FactTextField {
                    fact:               _camera.gimbalPitch
                    Layout.preferredWidth: ScreenTools.defaultFontPixelWidth * 6
                }
            }

            QGCLabel {
                text:           qsTr("Yaw")
                visible:        gimbalCheckBox.checked
            }

            RowLayout {
                visible:            gimbalCheckBox.checked
                Layout.fillWidth:   true
                spacing:            ScreenTools.defaultFontPixelWidth

                Slider {
                    Layout.fillWidth: true
                    minimumValue: -180
                    maximumValue: 180
                    value: _camera.gimbalYaw.value
                    onValueChanged: _camera.gimbalYaw.value = value
                }

                FactTextField {
                    fact:               _camera.gimbalYaw
                    Layout.preferredWidth: ScreenTools.defaultFontPixelWidth * 6
                }
            }
        }
    }
}
