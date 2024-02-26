'''
Instructions:
Keep the icons folder in the same directory as the script for the icons to be displayed in the visualizer widget.
Position the camera in the scene in the front of the model, to easily work with the visualizer widget. [Optional]
'''

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import maya.cmds as cmds
       
class AutoRiggerGUI(QDialog):
    '''
    The base class that handles the GUI for the Auto Rigger.
    '''
    def __init__(self):
        '''
        Initializes the GUI.
        '''
        super(AutoRiggerGUI, self).__init__()
        self.initUI()

    def initUI(self):
        '''
        Calls the methods to initialize the window, widgets, and layout.
        '''
        self.initWindow() 
        self.initTabs()       
        self.initLayout()
        self.initWidgets()

    def initWindow(self):
        self.setWindowTitle('Makra\'s Auto Rigger')
        screenSize = self.screen().size()
        self.setMinimumSize(screenSize.width()//6,screenSize.height()//2)

    def initTabs(self):
        '''
        Initializes two different tabs for markers and joints.
        '''
        self.tabs = QTabWidget(self)
        self.markersTab = QWidget()
        self.jointsTab = QWidget()

        self.tabs.addTab(self.markersTab, 'Markers')
        self.tabs.addTab(self.jointsTab, 'Joints')
        self.tabs.setTabEnabled(1, False)

    def initWidgets(self):
        '''
        Initializes the widgets for all the different parts of the body.
        '''
        # self.initVisualizer()
        self.initCreateMarkersWidgets()
        self.initAdjustMarkersWidgets()
        self.initLegsWidgets()
        self.initArmsWidgets()
        self.initSpineWidgets()
        self.initHeadWidgets()
        self.initRootWidgets()        

    def initLayout(self):
        '''
        Initializes the layout for the window.
        Creates the main layout, the visualizer layout, the skeleton guides layout, and the options layout.
        '''
        mainLayout = QHBoxLayout(self)     

        mainLayout.addWidget(self.tabs)   

        self.visualizerLayout = QVBoxLayout()
        self.skeletonGuidesLayout = QVBoxLayout()

        self.visualizerLayout.addLayout(self.skeletonGuidesLayout)

        self.jointsTabLayout = QVBoxLayout(self.jointsTab)
        self.markersTabLayout = QVBoxLayout(self.markersTab)
        self.markersTabLayout.setAlignment(Qt.AlignTop) 
        self.markersTab.setLayout(self.markersTabLayout)

        self.optionsLayout = QVBoxLayout()           

        mainLayout.addLayout(self.visualizerLayout)
        mainLayout.addLayout(self.optionsLayout)

        self.setLayout(mainLayout)

    def initVisualizer(self):
        '''
        Initializes the visualizer widget that is used to create the skeleton guides.
        It adds the icons for the different body parts that can be clicked and dragged to create the guides.
        ''' 
        self.visualizer = Visualizer(self)              

        dragHead = QLabel('Click-&-Drag', self)
        dragHead.move(20,20)

        parentDir = cmds.internalVar(userScriptDir=True) # directory where script is located, make sure to have the icons folder in the same directory as the script
        self.visualizer.addIcon(QPoint(60, 50), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/legL.png'), iconLabel= 'Legs')
        self.visualizer.addIcon(QPoint(110, 50), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/legR.png'))
        self.visualizer.addIcon(QPoint(60, 100), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/armL.png'), iconLabel= 'Arms')
        self.visualizer.addIcon(QPoint(110, 100), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/armR.png'))
        self.visualizer.addIcon(QPoint(60, 150), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/spine.png'), iconLabel= 'Spine')
        self.visualizer.addIcon(QPoint(60, 200), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/head.png'), iconLabel= 'Head')
        self.visualizer.addIcon(QPoint(60, 250), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/root.png'), iconLabel= 'Root')

        self.visualizer.showRig()

        self.createSkeletonGuidesBtn = QPushButton('Create Skeleton Guides')
               
        self.skeletonGuidesLayout.addWidget(self.createSkeletonGuidesBtn)        
        self.visualizerLayout.addWidget(self.visualizer)     

    def initCreateMarkersWidgets(self):
        '''
        Initializes the widgets that help in creating the markers for the skeleton guides.
        '''
        self.markers = None

        self.halfBodyRadioButton = QRadioButton('Half-Body')
        self.fullBodyRadioButton = QRadioButton('Full-Body')
        self.halfBodyRadioButton.setChecked(True)

        self.createMarkersBtn = QPushButton('Create Markers')
        self.createMarkersBtn.clicked.connect(self.onCreateMarkersBtnClicked)

        self.createMarkersGroupBox = QGroupBox('Create Markers')
        self.createMarkersLayout = QVBoxLayout()         

        self.createMarkersLayout.addWidget(self.halfBodyRadioButton)
        self.createMarkersLayout.addWidget(self.fullBodyRadioButton)
       
        self.createMarkersLayout.addWidget(self.createMarkersBtn)
        self.createMarkersGroupBox.setLayout(self.createMarkersLayout)

        self.markersTabLayout.addWidget(self.createMarkersGroupBox)

    def initAdjustMarkersWidgets(self):
        '''
        Initializes the widgets that help in adjusting the markers for the skeleton guides.
        '''
        self.editMarkersGroupBox = QGroupBox('Global Markers Adjustment')  
        self.editMarkersLayout = QVBoxLayout()
        self.editMarkersGroupBox.setDisabled(True)

        self.scaleLabel = QLabel('Scale:')

        self.scaleXSlider = CustomSlider(0, 1000, name='X: ')
        self.scaleYSlider = CustomSlider(0, 1000, name='Y: ')
        self.scaleZSlider = CustomSlider(0, 1000, name='Z: ')

        self.scaleXSlider.setValue(100)
        self.scaleYSlider.setValue(100)
        self.scaleZSlider.setValue(100)

        self.scaleXSlider.connectValueChanged(self.adjustMarkersScale)
        self.scaleYSlider.connectValueChanged(self.adjustMarkersScale)
        self.scaleZSlider.connectValueChanged(self.adjustMarkersScale)

        self.editMarkersLayout.addWidget(self.scaleLabel)
        self.editMarkersLayout.addWidget(self.scaleXSlider)
        self.editMarkersLayout.addWidget(self.scaleYSlider)
        self.editMarkersLayout.addWidget(self.scaleZSlider)

        self.offsetLabel = QLabel('Offset:')

        self.offsetXSlider = CustomSlider(-1000, 1000, name='X: ')
        self.offsetYSlider = CustomSlider(-1000, 1000, name='Y: ')
        self.offsetZSlider = CustomSlider(-1000, 1000, name='Z: ')

        self.offsetXSlider.connectValueChanged(self.adjustMarkersOffset)
        self.offsetYSlider.connectValueChanged(self.adjustMarkersOffset)
        self.offsetZSlider.connectValueChanged(self.adjustMarkersOffset)

        self.offsetXSlider.setValue(0)
        self.offsetYSlider.setValue(0)
        self.offsetZSlider.setValue(0)  

        self.editMarkersLayout.addWidget(self.offsetLabel)
        self.editMarkersLayout.addWidget(self.offsetXSlider)
        self.editMarkersLayout.addWidget(self.offsetYSlider)
        self.editMarkersLayout.addWidget(self.offsetZSlider)   

        self.rotationLabel = QLabel('Rotation:')

        self.rotXSlider = CustomSlider(0,360, name='X: ')
        self.rotYSlider = CustomSlider(0,360, name='Y: ')
        self.rotZSlider = CustomSlider(0,360, name='Z: ')

        self.rotXSlider.connectValueChanged(self.adjustMarkersRotation)
        self.rotYSlider.connectValueChanged(self.adjustMarkersRotation)
        self.rotZSlider.connectValueChanged(self.adjustMarkersRotation)

        self.rotXSlider.setValue(0)
        self.rotYSlider.setValue(0)
        self.rotZSlider.setValue(0)

        self.editMarkersLayout.addWidget(self.rotationLabel)
        self.editMarkersLayout.addWidget(self.rotXSlider)
        self.editMarkersLayout.addWidget(self.rotYSlider)
        self.editMarkersLayout.addWidget(self.rotZSlider)

        self.mirrorMarkersBtn = QPushButton('Mirror Markers')
        self.mirrorMarkersBtn.clicked.connect(self.onMirrorMarkersBtnClicked)

        self.editMarkersLayout.addWidget(self.mirrorMarkersBtn)

        self.editMarkersGroupBox.setLayout(self.editMarkersLayout)              
        self.markersTabLayout.addWidget(self.editMarkersGroupBox)

    def onCreateMarkersBtnClicked(self):
        '''
        When the create markers button is clicked, the markers are created, the joints tab and Adjust Markers group box is enabled.
        '''
        self.tabs.setTabEnabled(1, True)
        self.editMarkersGroupBox.setEnabled(True)
        self.createMarkersGroupBox.setDisabled(True)

        if self.halfBodyRadioButton.isChecked():
            markers = Markers.defaultBaseMarkers() + Markers.defaultLeftMarkers()
        else:
            markers = Markers.defaultBaseMarkers() + Markers.defaultLeftMarkers() + Markers.defaultRightMarkers()
            self.mirrorMarkersBtn.setEnabled(False)

        self.markers = Markers.createMarkers(markers)

    def onMirrorMarkersBtnClicked(self):
        '''
        When the mirror markers button is clicked, the current markers are mirrored.
        '''
        self.mirrorMarkersBtn.setEnabled(False)

        for marker in cmds.listRelatives(self.markers, children=True):
            if marker.endswith('_l'):
                rightMarker = marker.replace('_l', '_r')
                cmds.duplicate(marker, n=rightMarker)
                cmds.setAttr(rightMarker + '.tx', -cmds.getAttr(marker + '.tx'))     

    def initLegsWidgets(self):
        '''
        Initializes the widgets required for the Legs section.
        It also creates a group box to contain the widgets and sets the layout for the group box.
        Finally, it adds the group box to the options layout.
        '''
        self.legsIkRadioBtn = QRadioButton('IK')
        self.legsFkRadioBtn = QRadioButton('FK')
        self.legsIkFkRadioBtn = QRadioButton('IK/FK')

        self.legsFkRadioBtn.setChecked(True)

        self.legsSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.legsReverseFootIkCheckbox = QCheckBox('Reverse Foot IK')
        self.legsStretchyCheckbox = QCheckBox('Stretchy')

        self.legsCreateLegsJointsBtn = QPushButton('Create Joints')

        self.legsGroupBox = QGroupBox('LEGS')

        self.legsGroupBox.setLayout(self.createSectionLayout(
            [self.legsIkRadioBtn, self.legsFkRadioBtn, self.legsIkFkRadioBtn],
            [self.legsSpaceSwitchingCheckbox, self.legsReverseFootIkCheckbox, self.legsStretchyCheckbox],
            self.legsCreateLegsJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.legsGroupBox)

        # self.optionsLayout.addWidget(self.legsGroupBox)

    def initArmsWidgets(self):
        '''
        Initializes the widgets required for the Arms section.
        '''
        self.armsIkRadioBtn = QRadioButton('IK')
        self.armsFkRadioBtn = QRadioButton('FK')
        self.armsIkFkRadioBtn = QRadioButton('IK/FK')

        self.armsFkRadioBtn.setChecked(True)

        self.armsSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.armsWristRollCheckbox = QCheckBox('Wrist Roll')
        self.armsStretchyCheckbox = QCheckBox('Stretchy')

        self.createArmsJointsBtn = QPushButton('Create Joints')

        self.armsGroupBox = QGroupBox('ARMS')

        self.armsGroupBox.setLayout(self.createSectionLayout(
            [self.armsIkRadioBtn, self.armsFkRadioBtn, self.armsIkFkRadioBtn],
            [self.armsSpaceSwitchingCheckbox, self.armsWristRollCheckbox, self.armsStretchyCheckbox],
            self.createArmsJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.armsGroupBox)

        # self.optionsLayout.addWidget(self.armsGroupBox)

    def initSpineWidgets(self):
        '''
        Initializes the widgets required for the Spine section.
        '''
        self.spineSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.spineStretchyCheckbox = QCheckBox('Stretchy')

        self.createSpineJointsBtn = QPushButton('Create Joints')

        self.spineGroupBox = QGroupBox('SPINE')

        self.spineGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.spineSpaceSwitchingCheckbox, self.spineStretchyCheckbox],
            self.createSpineJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.spineGroupBox)

        # self.optionsLayout.addWidget(self.spineGroupBox)

    def initHeadWidgets(self):
        '''
        Initializes the widgets required for the Head section.
        '''
        self.headSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.headStretchyCheckbox = QCheckBox('Stretchy')

        self.createHeadJointsBtn = QPushButton('Create Joints')

        self.headGroupBox = QGroupBox('HEAD')

        self.headGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.headSpaceSwitchingCheckbox, self.headStretchyCheckbox],
            self.createHeadJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.headGroupBox)

        # self.optionsLayout.addWidget(self.headGroupBox)

    def initRootWidgets(self):
        '''
        Initializes the widgets required for the Root section.
        '''
        self.rootSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.rootStretchyCheckbox = QCheckBox('Stretchy')
        self.rootUniformScaleCheckbox = QCheckBox('Uniform Scale')

        self.createRootJointsBtn = QPushButton('Create Joints')

        self.rootGroupBox = QGroupBox('ROOT')

        self.rootGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.rootSpaceSwitchingCheckbox, self.rootStretchyCheckbox, self.rootUniformScaleCheckbox],
            self.createRootJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.rootGroupBox)

        # self.optionsLayout.addWidget(self.rootGroupBox)
   
    def createSectionLayout(self, radioButtons, checkBoxes, createButton):
        '''
        Since the layout for the different sections are similar, we use this modular method to create the layout for each section.
        '''
        sectionLayout = QVBoxLayout()

        if radioButtons:
            radioButtonLayout = QHBoxLayout()
            for radioButton in radioButtons:
                radioButtonLayout.addWidget(radioButton)
            sectionLayout.addLayout(radioButtonLayout)

        if checkBoxes:
            checkboxLayout = QHBoxLayout()
            for checkBox in checkBoxes:
                checkboxLayout.addWidget(checkBox)
            sectionLayout.addLayout(checkboxLayout)

        sectionLayout.addWidget(createButton)

        return sectionLayout
    
    def adjustMarkersScale(self):
        '''
        Adjusts the scale of the markers for the skeleton guides.
        '''
        cmds.scale(float(self.scaleXSlider.value())/100, float(self.scaleYSlider.value())/100, float(self.scaleZSlider.value())/100, self.markers)

    def adjustMarkersOffset(self):
        '''
        Adjusts the offset of the markers for the skeleton guides.
        '''
        cmds.xform(self.markers, translation=(float(self.offsetXSlider.value()), float(self.offsetYSlider.value()), float(self.offsetZSlider.value())))

    def adjustMarkersRotation(self):
        '''
        Adjusts the rotation of the markers for the skeleton guides.
        '''
        cmds.xform(self.markers, rotation=(float(self.rotXSlider.value()), float(self.rotYSlider.value()), float(self.rotZSlider.value())))
    
class Visualizer(QLabel):
    '''
    This class represents the visualizer widget that is used to create the skeleton guides.
    '''
    def __init__(self, parent=None):
        '''
        Initializes the GUI of visualizer widget.
        '''
        super(Visualizer, self).__init__(parent)
        self.initUI()

    def initUI(self):
        '''
        Sets the frame style, alignment and minimum size for the visualizer widget.
        '''
        self.setFrameStyle(QFrame.Sunken | QFrame.Panel)
        self.screenSize = self.screen().size()
        self.setMinimumSize(self.screenSize.width()//6,self.screenSize.height()//2)
        self.setAlignment(Qt.AlignCenter)

    def addIcon(self, position, iconLabel = None, iconPath=None):  
        '''
        Method to add an icon to the visualizer widget.
        Icons could have a label or not.
        '''     
        icon = DraggableIcon(self, iconPath)
        icon.move(position)
        icon.show()

        if iconLabel is not None:
            label = QLabel(iconLabel, self)
            label.move(position + QPoint(-(icon.width() + 20), 0))  # hardcoded for now
            label.show()

    def showRig(self): 
        '''
        Displays the rig in the visualizer widget.
        Currently, it takes a playblast of the current frame and displays it in the visualizer widget.
        So the user needs to repostion the camera in the model view so that they can work easily with the visualizer.
        '''      
        displayImg = cmds.playblast(completeFilename=True, format='image', 
                        width=self.screenSize.width()//3, 
                        height=self.screenSize.height(), 
                        showOrnaments=False, 
                        frame=cmds.currentTime(q=True), 
                        viewer=False, 
                        offScreen=True)        
        
        self.setPixmap(QPixmap(displayImg))

class CustomSlider(QWidget):
    def __init__(self, minimum, maximum, parent=None, name=None):
        super(CustomSlider, self).__init__(parent)
        self.initUI(name, minimum, maximum)

    def initUI(self, name, minimum, maximum):
        if name is not None:
            self.nameLabel = QLabel(name, self)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(minimum)
        
        self.minLabel = QLabel(str(minimum), self)
        self.maxLabel = QLabel(str(maximum), self)
        self.currentValue = QLineEdit(str(minimum), self)
        self.currentValue.setFixedWidth(60)

        self.currentValue.setValidator(QDoubleValidator(minimum, 99999, 2))
        
        self.slider.valueChanged.connect(self.updateCurrentValue)
        self.currentValue.textChanged.connect(self.updateSliderValue)

        layout = QHBoxLayout(self)
        if name is not None:
            layout.addWidget(self.nameLabel)
        layout.addWidget(self.minLabel)
        layout.addWidget(self.slider)
        layout.addWidget(self.maxLabel)
        layout.addWidget(self.currentValue)

        self.setLayout(layout)

    def updateCurrentValue(self, value):
        self.currentValue.setText(str(value))
    
    def updateSliderValue(self):
        value = int(float(self.currentValue.text()))
        self.slider.setValue(int(value))
    
    def setValue(self, value):
        self.slider.setValue(value)
    
    def value(self):
        return self.slider.value()
    
    def connectValueChanged(self, func):
        self.slider.valueChanged.connect(func)
        self.currentValue.textChanged.connect(func)

class DraggableIcon(QLabel):
    '''
    This class represents the draggable icons that are used to create the skeleton guides.
    '''
    def __init__(self, parent=None, iconPath=None):
        '''
        The variables get initialized and the icon is set.
        '''
        super(DraggableIcon, self).__init__(parent)
        self.setFixedSize(30, 30)  # hardcoded for now
        self.iconPath = iconPath
        self.dragging = False
        self.setPixmap(QPixmap(iconPath).scaled(self.size()))  

    def mousePressEvent(self, event):
        '''
        When mouse is clicked on an icon
        '''
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragStartPosition = event.pos() # record init pos of drag

    def mouseMoveEvent(self, event):
        '''
        When icon is being dragged
        '''
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.dragStartPosition)) # move icon with mouse

    def mouseReleaseEvent(self, event):
        '''
        When mouse is released after dragging
        '''
        self.dragging = False # stop dragging

class Markers:
    '''
    Static class that contains helper methods that are used in the auto rigging process.
    '''
    @staticmethod
    def defaultBaseMarkers():
        '''
        Returns the base markers for the skeleton guides.
        '''
        return [
            ('root', (0, 0, 0)), ('pelvis', (0, 105, 0)), ('spine1', (0, 125, 5)),
            ('spine2', (0, 138, 2.5)), ('spine3', (0, 150, -4.5)), ('neck', (0, 158.5, -3)),
            ('head', (0, 181.5, 1))
        ]
    
    @staticmethod
    def defaultLeftMarkers():
        '''
        Returns the left markers for the skeleton guides.        
        '''
        return [
            ('clavicle_l', (14, 149.5, -4.5)), ('upperArm_l', (23.5, 145.5, -4.5)),
            ('lowerArm_l', (36, 129, -5.5)), ('hand_l', (58.5, 110, 5)),
            ('thigh_l', (9, 95, 1)), ('knee_l', (14, 55, 0)), ('foot_l', (15.5, 15.5, -6)),
            ('ball_l', (17, 3.5, 5)), ('toe_l', (17, 3.5, 15.5))
        ]
    
    @staticmethod
    def defaultRightMarkers():
        '''
        Returns the right markers for the skeleton guides.
        '''
        rightMarkers = []

        for name, (x, y, z) in Markers.defaultLeftMarkers():
            rightMarkers.append((name.replace('_l', '_r'), (-x, y, z)))

        return rightMarkers
    
    @staticmethod
    def createMarkers(markers):
        '''
        Creates the markers for the skeleton guides.
        '''
        locators = []

        for marker in markers:
            loc = cmds.spaceLocator(n=marker[0])[0]  # cmds.spaceLocator returns a list, take the first item
            cmds.move(marker[1][0], marker[1][1], marker[1][2], loc)  # Position the locator
            locators.append(loc)

        group = cmds.group(locators, name="MarkersGrp")
        cmds.xform(group, pivots=(0, 0, 0), worldSpace=True)
        
        return group

arGUI = AutoRiggerGUI() # Create an instance of the AutoRiggerGUI class and show it
arGUI.show()