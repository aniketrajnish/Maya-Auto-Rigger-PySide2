'''
Click on IK button to create IK handles and controllers for the legs and arms.
Legs one is most likely incorrect, but the arms one is similar to class example.
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
        self.initCreateMarkersWidgets()
        self.initAdjustMarkersWidgets()
        self.initCreateSkeletonWidgets()
        self.initRootWidgets()
        self.initSpineWidgets()
        self.initHeadWidgets()
        self.initArmsWidgets()
        self.initLegsWidgets()

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
        self.editMarkersGroupBox.setDisabled(True) # every part of the rig creation process is divided into group boxes, 
                                                   # and they are disabled until the previous step is completed to avoid errors
        def createCustomSlider(name, min, max, init, connection):
            slider = CustomSlider(min, max, name=name)
            slider.setValue(init)
            slider.connectValueChanged(connection)
            self.editMarkersLayout.addWidget(slider)
            return slider

        self.scaleLabel = QLabel('Scale:')
        self.editMarkersLayout.addWidget(self.scaleLabel)

        self.scaleXSlider = createCustomSlider('X: ', 0, 1000, 100, self.adjustMarkersScale)
        self.scaleYSlider = createCustomSlider('Y: ', 0, 1000, 100, self.adjustMarkersScale)
        self.scaleZSlider = createCustomSlider('Z: ', 0, 1000, 100, self.adjustMarkersScale)

        self.offsetLabel = QLabel('Offset:')
        self.editMarkersLayout.addWidget(self.offsetLabel)

        self.offsetXSlider = createCustomSlider('X: ', -1000, 1000, 0, self.adjustMarkersOffset)
        self.offsetYSlider = createCustomSlider('Y: ', -1000, 1000, 0, self.adjustMarkersOffset)
        self.offsetZSlider = createCustomSlider('Z: ', -1000, 1000, 0, self.adjustMarkersOffset)


        self.rotationLabel = QLabel('Rotation:')
        self.editMarkersLayout.addWidget(self.rotationLabel)

        self.rotXSlider = createCustomSlider('X: ', 0, 360, 0, self.adjustMarkersRotation)
        self.rotYSlider = createCustomSlider('Y: ', 0, 360, 0, self.adjustMarkersRotation)
        self.rotZSlider = createCustomSlider('Z: ', 0, 360, 0, self.adjustMarkersRotation)
        
        self.mirrorMarkersBtn = QPushButton('Mirror Markers')
        self.mirrorMarkersBtn.clicked.connect(self.onMirrorMarkersBtnClicked)

        self.editMarkersLayout.addWidget(self.mirrorMarkersBtn)

        self.editMarkersGroupBox.setLayout(self.editMarkersLayout)              
        self.markersTabLayout.addWidget(self.editMarkersGroupBox)

    def onCreateMarkersBtnClicked(self):
        '''
        When the create markers button is clicked, the markers are created, the joints tab and Adjust Markers group box is enabled.
        '''
        modelPanels = [panel for panel in cmds.getPanel(all=True) if cmds.getPanel(typeOf=panel) == 'modelPanel']
        
        for panel in modelPanels:
            cmds.modelEditor(panel, edit=True, displayAppearance='wireframe') # change the display of the model panel to wireframe to make it easier to see the markers

        self.editMarkersGroupBox.setEnabled(True)
        self.createMarkersGroupBox.setDisabled(True)        

        if self.halfBodyRadioButton.isChecked():
            markers = Markers.defaultBaseMarkers() + Markers.defaultLeftMarkers()
        else:
            markers = Markers.defaultBaseMarkers() + Markers.defaultLeftMarkers() + Markers.defaultRightMarkers()
            self.mirrorMarkersBtn.setEnabled(False)
            self.tabs.setTabEnabled(1, True)

        self.markers = Markers.createMarkers(markers)
        self.updateMarkerData() # update marker data after creating the markers

    def updateMarkerData(self):
        '''
        Updates the marker data.
        '''
        self.markerData = {} # dictionary to store marker data in the same format of the default markers
        self.markerNames = cmds.listRelatives(self.markers, children=True)

        for markerName in self.markerNames:
            self.markerData[markerName] = cmds.xform(markerName, q=True, translation=True)

    def onMirrorMarkersBtnClicked(self):
        '''
        When the mirror markers button is clicked, the current markers are mirrored.
        '''
        self.mirrorMarkersBtn.setEnabled(False)
        self.tabs.setTabEnabled(1, True)

        for marker in self.markerNames:
            if marker.endswith('_l'):
                rightMarker = marker.replace('_l', '_r')
                cmds.duplicate(marker, n=rightMarker)
                cmds.setAttr(rightMarker + '.tx', -cmds.getAttr(marker + '.tx'))  
        
        self.updateMarkerData()

    def initCreateSkeletonWidgets(self):
        '''
        Initializes the widgets required to create the skeleton.
        '''
        self.createSkeletonBtn = QPushButton('Create Skeleton')
        self.createSkeletonBtn.clicked.connect(self.onCreateSkeletonBtnClicked)

        self.jointsTabLayout.addWidget(self.createSkeletonBtn)

    def onCreateSkeletonBtnClicked(self):
        '''
        When the create skeleton guides button is clicked, the skeleton is created.
        '''
        self.updateMarkerData()
        
        modelPanels = [panel for panel in cmds.getPanel(all=True) if cmds.getPanel(typeOf=panel) == 'modelPanel']
        
        for panel in modelPanels:
            cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded') # change the display of the model panel back to smooth shaded

        self.skeleton = Skeleton.createSkeleton(self.markerData)
        cmds.delete(self.markers)

        self.rootGroupBox.setEnabled(True)

    # def initHW7Widgets(self):        
    #     '''
    #     Temporary method to show the HW7 FK rig.
    #     '''       
    #     self.hw7Button = QPushButton('Show FK Rig for HW7')
    #     self.hw7Button.clicked.connect(self.onHW7ButtonClicked)

    #     self.jointsTabLayout.addWidget(self.hw7Button)

    #     self.legsGroupBox.setDisabled(True)
    #     self.armsGroupBox.setDisabled(True)
    #     self.spineGroupBox.setDisabled(True)
    #     self.headGroupBox.setDisabled(True)
    #     self.rootGroupBox.setDisabled(True)

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

        self.createLegsJointsBtn = QPushButton('Create Controllers')
        self.createLegsJointsBtn.clicked.connect(self.onCreateLegsControllersBtnClicked)

        self.legsGroupBox = QGroupBox('LEGS')

        self.legsGroupBox.setLayout(self.createSectionLayout(
            [self.legsIkRadioBtn, self.legsFkRadioBtn, self.legsIkFkRadioBtn],
            [self.legsSpaceSwitchingCheckbox, self.legsReverseFootIkCheckbox, self.legsStretchyCheckbox],
            self.createLegsJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.legsGroupBox)
        self.legsGroupBox.setDisabled(True) 

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

        self.createArmsJointsBtn = QPushButton('Create Controllers')
        self.createArmsJointsBtn.clicked.connect(self.onCreateArmsControllersBtnClicked)

        self.armsGroupBox = QGroupBox('ARMS')

        self.armsGroupBox.setLayout(self.createSectionLayout(
            [self.armsIkRadioBtn, self.armsFkRadioBtn, self.armsIkFkRadioBtn],
            [self.armsSpaceSwitchingCheckbox, self.armsWristRollCheckbox, self.armsStretchyCheckbox],
            self.createArmsJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.armsGroupBox)
        self.armsGroupBox.setDisabled(True)

        # self.optionsLayout.addWidget(self.armsGroupBox)

    def initSpineWidgets(self):
        '''
        Initializes the widgets required for the Spine section.
        '''
        self.spineSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.spineStretchyCheckbox = QCheckBox('Stretchy')

        self.createSpineJointsBtn = QPushButton('Create Controllers')
        self.createSpineJointsBtn.clicked.connect(self.onCreateSpineControllersBtnClicked)

        self.spineGroupBox = QGroupBox('SPINE')

        self.spineGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.spineSpaceSwitchingCheckbox, self.spineStretchyCheckbox],
            self.createSpineJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.spineGroupBox)
        self.spineGroupBox.setDisabled(True)

        # self.optionsLayout.addWidget(self.spineGroupBox)

    def initHeadWidgets(self):
        '''
        Initializes the widgets required for the Head section.
        '''
        self.headSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.headStretchyCheckbox = QCheckBox('Stretchy')

        self.createHeadJointsBtn = QPushButton('Create Controllers')
        self.createHeadJointsBtn.clicked.connect(self.onCreateHeadControllersBtnClicked)

        self.headGroupBox = QGroupBox('HEAD')

        self.headGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.headSpaceSwitchingCheckbox, self.headStretchyCheckbox],
            self.createHeadJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.headGroupBox)
        self.headGroupBox.setDisabled(True)

        # self.optionsLayout.addWidget(self.headGroupBox)

    def initRootWidgets(self):
        '''
        Initializes the widgets required for the Root section.
        '''
        self.rootSpaceSwitchingCheckbox = QCheckBox('Space Switching')
        self.rootStretchyCheckbox = QCheckBox('Stretchy')
        self.rootUniformScaleCheckbox = QCheckBox('Uniform Scale')

        self.createRootJointsBtn = QPushButton('Create Controllers')
        self.createRootJointsBtn.clicked.connect(self.onCreateRootControllersBtnClicked)

        self.rootGroupBox = QGroupBox('ROOT')

        self.rootGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.rootSpaceSwitchingCheckbox, self.rootStretchyCheckbox, self.rootUniformScaleCheckbox],
            self.createRootJointsBtn
        ))

        self.jointsTabLayout.addWidget(self.rootGroupBox)
        self.rootGroupBox.setDisabled(True)

        # self.optionsLayout.addWidget(self.rootGroupBox)

    def onCreateLegsControllersBtnClicked(self):
        '''
        When the create legs controllers button is clicked, the legs controllers are created.
        '''
        if self.legsFkRadioBtn.isChecked(): # FK
            self.leftLegControls = FK.createFKCharacterControllers('thigh_l', controllerRadius=13)
            self.rightLegControls = FK.createFKCharacterControllers('thigh_r', controllerRadius=13)

            cmds.parent(self.leftLegControls[0] + '_parent', self.rootControls[-1])
            cmds.parent(self.rightLegControls[0] + '_parent', self.rootControls[-1])

        elif self.legsIkRadioBtn.isChecked(): # IK
            for side in ['_l', '_r']:
                IK.createStartJointController('thigh' + side, self.rootControls[1], 'thigh' + side, name = 'thigh' + side, controllerRadius=15)
                handle, effector = IK.createIKHandle('thigh' + side, 'foot' + side, 'leg_ik' + side)
                IK.createIKController(handle, 'ball' + side, self.rootControls[0] + '_parent', name = 'leg' + side, controllerRadius=8)
                IK.createPoleVectorConstraint(handle, self.rootControls[0] + '_parent', 'knee' + side, name = 'pv_leg_' + side, controllerRadius=15)  

            # self.creatFootControllers('ball', 'ctrl_leg')


        elif self.legsIkFkRadioBtn.isChecked():
            for side in ['_l', '_r']:
                legChain = ['thigh' + side, 'knee' + side, 'foot' + side]
                FKIK.createFKIKAccessories(legChain, 'leg' + side, controllerRadius=13, 
                                           fkParent=self.rootControls[1], ikParent=self.rootControls[0] + '_parent', 
                                           ikStartParent= self.rootControls[1])

            # self.creatFootControllers('ball')

        self.legsGroupBox.setDisabled(True)
        self.cleanup() # organize the rig in the outliner

    def onCreateArmsControllersBtnClicked(self):
        '''
        When the create arms controllers button is clicked, the arms controllers are created.
        '''
        if self.armsFkRadioBtn.isChecked(): # FK
            self.leftArmControls = FK.createFKCharacterControllers('clavicle_l',controllerRadius=8)
            self.rightArmControls = FK.createFKCharacterControllers('clavicle_r',controllerRadius=8)

            cmds.parent(self.leftArmControls[0] + '_parent', self.spineControls[-1])
            cmds.parent(self.rightArmControls[0] + '_parent', self.spineControls[-1])
        
        elif self.armsIkRadioBtn.isChecked(): # IK
            for side in ['_l', '_r']:
                IK.createStartJointController('clavicle' + side, self.spineControls[-1], 'upperArm' + side, name = 'clavicle' + side, controllerRadius=12)
                handle, effector = IK.createIKHandle('upperArm' + side, 'hand' + side,'arm_ik' + side)
                self.ikControl = IK.createIKController(handle,'hand' + side, self.rootControls[0] + '_parent', name = 'arm' + side, controllerRadius=8)
                IK.createPoleVectorConstraint(handle, self.rootControls[0] + '_parent', 'lowerArm' + side, name = 'pv_arm_' + side, controllerRadius=8)
                
            # self.createFingerControllers('thumb', 'ctrl_arm')
            # self.createFingerControllers('index', 'ctrl_arm')
            # self.createFingerControllers('middle', 'ctrl_arm')

        elif self.armsIkFkRadioBtn.isChecked(): # IK/FK
            for side in ['_l', '_r']:
                armChain = ['clavicle' + side, 'upperArm' + side, 'lowerArm' + side, 'hand' + side]
                FKIK.createFKIKAccessories(armChain, 'arm' + side, controllerRadius=8, 
                                           fkParent=self.spineControls[-1], ikParent=self.rootControls[0] + '_parent', 
                                           ikStartParent= self.spineControls[-1], ikOffset=1)

            # self.createFingerControllers('thumb')
            # self.createFingerControllers('index')
            # self.createFingerControllers('middle')    


        self.armsGroupBox.setDisabled(True)
        self.legsGroupBox.setEnabled(True)

    def creatFootControllers(self, foot, parent = None):
        '''
        Creates the foot controllers.
        '''
        for side in ['_l', '_r']:
            footControls = FK.createFKCharacterControllers(rootJoint = foot + side, controllerRadius=8)
            cmds.parent(footControls[0] + '_parent', parent + side + '_parent')

    def createFingerControllers(self, finger, parent = None):
        '''
        Creates the finger controllers.
        '''
        for side in ['_l', '_r']:
            fingerControls = FK.createFKCharacterControllers(rootJoint = finger + '1' + side, endJoint = finger + '3' + side, controllerRadius=3)
            if parent:
                cmds.parent(fingerControls[0] + '_parent', parent + side + '_parent')

    def onCreateSpineControllersBtnClicked(self):
        '''
        When the create spine controllers button is clicked, the spine controllers are created.
        '''
        self.spineControls = FK.createFKCharacterControllers(rootJoint='spine1', endJoint='spine3')

        cmds.parent(self.spineControls[0] + '_parent', self.rootControls[-1])

        self.spineGroupBox.setDisabled(True)
        self.headGroupBox.setEnabled(True)

    def onCreateHeadControllersBtnClicked(self):
        '''
        When the create head controllers button is clicked, the head controllers are created.
        '''
        self.headControls = FK.createFKCharacterControllers('neck', controllerRadius=10)

        cmds.parent(self.headControls[0] + '_parent', self.spineControls[-1])

        self.headGroupBox.setDisabled(True)
        self.armsGroupBox.setEnabled(True)

    def onCreateRootControllersBtnClicked(self):
        '''
        When the create root controllers button is clicked, the root controllers are created.
        '''
        self.rootControls = FK.createFKCharacterControllers(rootJoint='root', endJoint='pelvis')

        self.rootGroupBox.setDisabled(True)
        self.spineGroupBox.setEnabled(True)

    # def onHW7ButtonClicked(self):
    #     '''
    #     When the HW7 button is clicked, the HW7 FK rig is shown, this is temporary.
    #     '''                
    #     self.updateMarkerData()
        
    #     modelPanels = [panel for panel in cmds.getPanel(all=True) if cmds.getPanel(typeOf=panel) == 'modelPanel']
        
    #     for panel in modelPanels:
    #         cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded')

    #     skels = Skeleton.createSkeleton(self.markerData)
    #     cmds.delete(self.markers)
    #     FK.createFKCharacterControllers(skels[0])        
   
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

    def cleanup(self):
        '''
        Organizes the rig in the outliner.
        '''
        parentGrp = cmds.group(em=True, n='rig')
        cmds.parent(self.rootControls[0] + '_parent', parentGrp)
        cmds.parent(self.skeleton[0], parentGrp)
        
        for side in ['_l', '_r']: # send the ik handle in the controllers group
            if cmds.objExists('leg_ik' + side):
                cmds.parent('leg_ik' + side, self.rootControls[0] + '_parent')
            if cmds.objExists('arm_ik' + side):
                cmds.parent('arm_ik' + side, self.rootControls[0] + '_parent')
            if cmds.objExists('leg' + side + '_ik'):
                cmds.parent('leg' + side + '_ik', parentGrp)
            if cmds.objExists('arm' + side + '_ik'):
                cmds.parent('arm' + side + '_ik', parentGrp)   
    
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
    '''
    A class to create a custom slider that I've tried replicating from the Maya cmds UI.
    '''
    def __init__(self, minimum, maximum, parent=None, name=None):
        '''
        Initializes the custom slider and sets the range, value.
        '''
        super(CustomSlider, self).__init__(parent)
        self.initUI(name, minimum, maximum)

    def initUI(self, name, minimum, maximum):
        '''
        Create the custom slider using PyQt's GUI classes, make it look like the Maya cmds slider.
        '''
        if name is not None:
            self.nameLabel = QLabel(name, self)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(minimum)
        
        self.minLabel = QLabel(str(minimum), self)
        self.maxLabel = QLabel(str(maximum), self)
        self.currentValue = QLineEdit(str(minimum), self)
        self.currentValue.setFixedWidth(60)

        self.currentValue.setValidator(QDoubleValidator(minimum, 99999, 2)) # why don't they allow for float(inf) as max value? :/
        
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
        '''
        Updates the text field with the current value of the slider.
        '''
        self.currentValue.setText(str(value))
    
    def updateSliderValue(self):
        '''
        Updates the slider with the current value of the text field.
        '''
        value = int(float(self.currentValue.text()))
        self.slider.setValue(int(value))
    
    def setValue(self, value):
        '''
        Sets the value of the slider.
        '''
        self.slider.setValue(value)
    
    def value(self):
        '''
        Returns current value.
        '''
        return self.slider.value()
    
    def connectValueChanged(self, func):
        '''
        Connects the valueChanged signal to a delegate function.
        '''
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

class FKIK:
    '''
    Creates FKIK switches and controls for the arms and legs.
    '''
    @staticmethod
    def duplicateChain(jointChain, prefix):
        '''
        Duplicates a joint chain and adds a prefix to the new chain.
        For the purpose of creating the FKIK switches.
        '''
        dupChain = []

        for joint in jointChain:
            dupJoint = cmds.duplicate(joint, po=True, n= prefix + '_' + joint)[0]
            dupChain.append(dupJoint)

        for i in range(len(dupChain)-1):
            cmds.parent(dupChain[i+1], dupChain[i])

        return dupChain       
    
    @staticmethod
    def createFKIKAccessories(jointChain, prefix, controllerRadius = 20, fkParent=None, ikParent=None, ikStartParent=None, ikOffset=0):
        '''
        Given a joint chain, it creates the FKIK switch.
        '''
        fkChain = FKIK.duplicateChain(jointChain, 'fk_' + prefix)
        ikChain = FKIK.duplicateChain(jointChain, 'ik_' + prefix)

        fkCntrls = FK.createFKCharacterControllers(fkChain[0], parent=None, endJoint=fkChain[-1], controllerRadius=controllerRadius)
        cmds.parent(fkCntrls[0] + '_parent', fkParent)

        startCntrl = IK.createStartJointController(ikChain[0], ikStartParent, ikChain[ikOffset], prefix + '_start_ik', controllerRadius=controllerRadius)
        ikHandle, effector = IK.createIKHandle(ikChain[ikOffset], ikChain[-1], prefix + '_ik')
        ikCntrl = IK.createIKController(ikHandle, ikChain[-1], ikParent, prefix + '_ik', controllerRadius=controllerRadius)
        pvJoint = cmds.listRelatives(ikChain[-1], parent=True)[0]
        pvCntrl = IK.createPoleVectorConstraint(ikHandle, ikParent, pvJoint, prefix + '_pv', controllerRadius=controllerRadius)

        return fkCntrls, ikCntrl, pvCntrl        
    
    @staticmethod
    def createFKIKSwitch(jointChain, fkCntrls, ikCntrl, pvCntrl, switchName):
        '''
        Creates the FKIK switch.
        '''
        switchCtrl = cmds.circle(n=switchName, nr=(0,0,1), c=(0, 0, 0), r=20)[0]
        cmds.delete(cmds.parentConstraint(jointChain[-1], switchCtrl))

        cmds.addAttr(switchCtrl, ln='FKIK_Switch', at='enum', en='fk:ik:', k=True)

        for fkCntrl in fkCntrls:
            cmds.connectAttr(switchCtrl + '.FKIK_Switch', fkCntrl + '.visibility', f=True)
        cmds.connectAttr(switchCtrl + '.FKIK_Switch', ikCntrl + '.visibility', f=True)
        cmds.connectAttr(switchCtrl + '.FKIK_Switch', pvCntrl + '.visibility', f=True)

        Helpers.lockAndHide(switchCtrl, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        return switchCtrl

class IK:
    '''
    Tried replicating the IK class from the class example, hopefully it works.
    '''
    @staticmethod
    def createIKHandle(startJoint, endEffector, name = ''):
        '''
        Creates an IK handle between the start joint and the end effector.
        '''
        handle, effector = cmds.ikHandle(sj=startJoint, ee=endEffector, n=name, sol='ikRPsolver')
        return handle, effector
    
    @staticmethod
    def createPoleVectorConstraint(ikHandle, parent, joint, name = '', controllerRadius = 20):
        '''
        Creates a pole vector constraint between the pole vector and the IK handle.
        '''
        poleVector = cmds.circle(n='ctrl_' + name, nr=(1, 0, 0), c=(0, 0, 0), r=controllerRadius)[0]

        cmds.pointConstraint(joint, poleVector)
        cmds.delete(poleVector, cn=True)

        cmds.poleVectorConstraint(poleVector, ikHandle)
        cmds.parent(poleVector, parent)

        return poleVector
    
    @staticmethod
    def createStartJointController(joint, parent, child, name = '', controllerRadius = 20):
        '''
        Creates a controller for the start joint of the IK handle.
        '''
        controller = cmds.circle(n='ctrl_' + name, nr=(1, 0, 0), c=(0, 0, 0), r=controllerRadius)[0]

        cmds.pointConstraint(child, controller)
        cmds.delete(controller, cn=True)

        cmds.parent(controller, parent)
        cmds.makeIdentity(controller, apply=True, r=True, s=True, t=True, n=False, pn=True)
        cmds.delete(controller, ch=True)

        cmds.aimConstraint(controller, joint, mo=True, wut='None')
        Helpers.lockAndHide(controller, ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        return controller
    
    @staticmethod
    def createIKController(ikHandle, joint, parent, name = '', controllerRadius = 20):
        '''
        Creates an IK control for the IK handle.
        '''
        controller = cmds.circle(n='ctrl_' + name, nr=(1, 0, 0), c=(0, 0, 0), r=controllerRadius)[0]

        ctrlParent = cmds.group(em=True, n='ctrl_' + name + '_parent')
        cmds.parent(controller, ctrlParent)

        cmds.pointConstraint(joint, ctrlParent, mo=False)
        cmds.orientConstraint(joint, ctrlParent, mo=False)

        cmds.delete(ctrlParent, cn=True)
        cmds.makeIdentity(controller, apply=True, r=True, s=True, t=True, n=False, pn=True)
        
        cmds.pointConstraint(controller, ikHandle, mo=True)
        cmds.orientConstraint(controller, joint, mo=True)
        cmds.parent(ctrlParent, parent)

        return controller

class FK:
    '''
    Static class that allows for the creation of the FK controllers.
    '''
    @staticmethod
    def createFKController(jName, pName = None, controllerRadius = 20):
        ''' 
        FK controller creation. 
        '''
        controller = cmds.circle(n='ctrl_' + jName, nr=(1, 0, 0), c=(0, 0, 0), r=controllerRadius)[0]
        
        ctrlParent = cmds.group(em=True, n='ctrl_' + jName + '_parent')
        cmds.parent(controller, ctrlParent)

        cmds.pointConstraint(jName, ctrlParent, mo=False)
        cmds.orientConstraint(jName, ctrlParent, mo=False)

        cmds.delete(ctrlParent, cn=True)
        cmds.makeIdentity(controller, apply=True, r=True, s=True, t=True, n=False, pn=True)

        cmds.parentConstraint(controller, jName, mo=True)

        if pName:
            pController = 'ctrl_' + pName
            cmds.parent(ctrlParent, pController)

        return controller
    
    @staticmethod
    def createFKCharacterControllers(rootJoint = None, parent = None, endJoint = None, controllerRadius = 20):
        '''
        Recursevly traverse the character skeleton and creates a default controller at every joint.
        '''  
        controllers = []
        controller = FK.createFKController(rootJoint, parent, controllerRadius)   
        controllers.append(controller)

        if endJoint is not None:        
            if rootJoint == endJoint:
                return controllers

        kids = cmds.listRelatives(rootJoint, c=True, type='joint')

        if kids:
            for kid in kids:
               controllers.extend(FK.createFKCharacterControllers(kid, rootJoint, endJoint, controllerRadius))

        return controllers

class Skeleton:
    '''
    Static class that allows for the creation of the skeleton from the markers.
    '''
    @staticmethod
    def createJoint(jName = '', jParent = None, jPos = (0,0,0)):
        '''
        Creates a joint with the given name, parent, and position.
        '''
        cmds.select(clear=True)

        j = cmds.joint(n=jName, p=jPos)

        if jParent:
            cmds.parent(j, jParent)
            cmds.joint(jParent, e=True, zso=True, oj='xyz', sao='yup')

        cmds.select(j, r=True)
            
        return j
    
    @staticmethod
    def createJointFromMarker(markerName, markerData, jParent=None):
        '''
        Creates a joint between specified marker.
        '''
        pos = markerData[markerName]
        cmds.delete(markerName)
        return Skeleton.createJoint(jName=markerName, jParent=jParent, jPos=pos)
    
    @staticmethod
    def createJointChainFromMarkers(markerNames, markerData, jParent=None):
        '''
        Creates a joint chain between the specified markers.
        '''
        parent = jParent
        chain = []

        for markerName in markerNames:
            newJoint = Skeleton.createJointFromMarker(markerName, markerData, jParent=parent)
            parent = newJoint
            chain.append(newJoint)

        return chain
    
    @staticmethod
    def createSkeleton(markerData):
        '''Creates the skeleton from the given markers.'''
        baseMarkers = [marker[0] for marker in Markers.defaultBaseMarkers()]
        leftSideMarkers = [marker[0] for marker in Markers.defaultLeftMarkers()]
        rightSideMarkers = [marker[0] for marker in Markers.defaultRightMarkers()]

        rootJ = Skeleton.createJointFromMarker('root', markerData) # base joints
        pelvisJ = Skeleton.createJointFromMarker('pelvis', markerData, jParent=rootJ)
        spineJs = Skeleton.createJointChainFromMarkers(baseMarkers[2:], markerData, jParent=pelvisJ)

        leftArmJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[:4], markerData, jParent=spineJs[2]) # left joints
        leftThumbJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[4:7], markerData, jParent=leftArmJs[-1])
        leftIndexJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[7:10], markerData, jParent=leftArmJs[-1])
        leftMiddleJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[10:13], markerData, jParent=leftArmJs[-1])
        leftLegJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[13:], markerData, jParent=pelvisJ)

        rightArmJs = Skeleton.createJointChainFromMarkers(rightSideMarkers[:4], markerData, jParent=spineJs[2]) # right joints
        rightThumbJs = Skeleton.createJointChainFromMarkers(rightSideMarkers[4:7], markerData, jParent=rightArmJs[-1])
        rightIndexJs = Skeleton.createJointChainFromMarkers(rightSideMarkers[7:10], markerData, jParent=rightArmJs[-1])
        rightMiddleJs = Skeleton.createJointChainFromMarkers(rightSideMarkers[10:13], markerData, jParent=rightArmJs[-1])
        rightLegJs = Skeleton.createJointChainFromMarkers(rightSideMarkers[13:], markerData, jParent=pelvisJ)

        return rootJ, pelvisJ, spineJs, leftArmJs, leftThumbJs, leftIndexJs, leftMiddleJs, leftLegJs, rightArmJs, rightThumbJs, rightIndexJs, rightMiddleJs, rightLegJs

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
            ('root', (0, 0, 0)), ('pelvis', (0, 105, 0)), 
            ('spine1', (0, 125, 5)), ('spine2', (0, 138, 2.5)), ('spine3', (0, 150, -4.5)), 
            ('neck', (0, 158.5, -3)), ('head', (0, 181.5, 1))
        ]
    
    @staticmethod
    def defaultLeftMarkers():
        '''
        Returns the left markers for the skeleton guides.        
        '''
        return [
            ('clavicle_l', (14, 149.5, -4.5)), ('upperArm_l', (23.5, 145.5, -4.5)),
            ('lowerArm_l', (36, 129, -5.5)), ('hand_l', (58.5, 110, 5)),
            ('thumb1_l', (57, 106, 11.5)), ('thumb2_l', (57, 104.5, 15)), ('thumb3_l', (57.5, 102, 19)),
            ('index1_l', (64, 103, 12.5)), ('index2_l', (65, 98, 15)), ('index3_l', (64.5, 94.5, 17)),
            ('middle1_l', (65, 102, 9)), ('middle2_l', (66, 96.5, 11)), ('middle3_l', (62, 92, 12.5)),
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

            cmds.setAttr(loc + '.localScale', 5, 5, 5, type='double3')    

            locators.append(loc)        

        group = cmds.group(locators, name='MarkersGrp')
        cmds.xform(group, pivots=(0, 0, 0), worldSpace=True)
        
        return group
    
class Helpers:
    '''
    Static class that contains helper methods that are used in the auto rigging process.
    '''
    @staticmethod
    def lockAndHide(node, attributes):
        '''
        Locks and hides the given attributes of the given node.
        '''
        for attr in attributes:
            cmds.setAttr(node + '.' + attr, l=True, k=False, cb=False)
    
    @staticmethod
    def unlockAndShow(node, attributes):
        '''
        Unlocks and shows the given attributes of the given node.
        '''
        for attr in attributes:
            cmds.setAttr(node + '.' + attr, l = False, k = True, cb = True)

arGUI = AutoRiggerGUI() # Create an instance of the AutoRiggerGUI class and show it
arGUI.show()