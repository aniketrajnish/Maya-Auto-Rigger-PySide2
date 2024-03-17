'''
Implemented two advanced features: Spline Spine and Uniform Scaling
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
        self.setMinimumSize(screenSize.width()//6,screenSize.height()//1.6)

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
        self.initFKIKSnappingWidgets()

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

        self.splineSpineCheckbox = QCheckBox('Spline Spine') # keep spline spine option in the markers tab so that we can control the joint placement
        self.splineSpineCheckbox.setChecked(True)

        self.createMarkersBtn = QPushButton('Create Markers')
        self.createMarkersBtn.clicked.connect(self.onCreateMarkersBtnClicked)

        self.createMarkersGroupBox = QGroupBox('Create Markers')
        self.createMarkersLayout = QVBoxLayout()         

        self.createMarkersLayout.addWidget(self.halfBodyRadioButton)
        self.createMarkersLayout.addWidget(self.fullBodyRadioButton)
        self.createMarkersLayout.addWidget(self.splineSpineCheckbox)
       
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

        markers = Markers.defaultLeftMarkers() 

        self.splineSpine = False

        if self.splineSpineCheckbox.isChecked():
            markers += Markers.defaultSplineBaseMarkers()        
            self.splineSpine = True
        else:
            markers += Markers.defaultBaseMarkers()

        if self.fullBodyRadioButton.isChecked():
            markers += Markers.defaultRightMarkers()
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

        self.skeleton = Skeleton.createSkeleton(self.markerData, self.splineSpine)
        cmds.delete(self.markers)

        self.rootGroupBox.setEnabled(True)
        self.createSkeletonBtn.setDisabled(True)

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

        self.rootUniformScaleCheckbox.setChecked(True)

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
    
    def initFKIKSnappingWidgets(self):
        '''
        Initializes the widgets required for the FKIK snapping.
        Gets enabled after cleanup.
        '''
        self.fkIkSnappingGroupBox = QGroupBox('FK/IK Snapping')
        self.fkIkSnappingLayout = QVBoxLayout()

        self.fkikRadioBtn = QRadioButton('FK-IK')
        self.ikfkRadioBtn = QRadioButton('IK-FK')
        self.fkikRadioBtn.setChecked(True)

        self.snapOrderLayout = QHBoxLayout()
        self.snapOrderLayout.addWidget(self.fkikRadioBtn)
        self.snapOrderLayout.addWidget(self.ikfkRadioBtn)
        self.fkIkSnappingLayout.addLayout(self.snapOrderLayout)

        self.armsLayout = QHBoxLayout()
        self.lArmBtn = QPushButton('Left Arm')
        self.rArmBtn = QPushButton('Right Arm')
        self.armsLayout.addWidget(self.lArmBtn)
        self.armsLayout.addWidget(self.rArmBtn)
        self.lArmBtn.clicked.connect(lambda: self.snapArmFKIK('_l'))
        self.rArmBtn.clicked.connect(lambda: self.snapArmFKIK('_r'))

        self.legsLayout = QHBoxLayout()
        self.lLegBtn = QPushButton('Left Leg')
        self.rLegBtn = QPushButton('Right Leg')
        self.legsLayout.addWidget(self.lLegBtn)
        self.legsLayout.addWidget(self.rLegBtn)
        self.lLegBtn.clicked.connect(lambda: self.snapLegFKIK('_l'))
        self.rLegBtn.clicked.connect(lambda: self.snapLegFKIK('_r'))

        self.fkIkSnappingLayout.addLayout(self.armsLayout)
        self.fkIkSnappingLayout.addLayout(self.legsLayout)

        self.fkIkSnappingGroupBox.setLayout(self.fkIkSnappingLayout)
        self.jointsTabLayout.addWidget(self.fkIkSnappingGroupBox)

        self.fkIkSnappingGroupBox.setDisabled(True)
        
        self.isLegFKIK = False
        self.isArmFKIK = False

    def snapArmFKIK(self, side):
        '''
        Calls the snap methods for the arms.
        '''
        fkCntrls = self.armFkCntrls[side] 
        ikJoints = self.armIkChains[side]
        ikCntrls = [self.armStartCntrls[side], self.armIkCntrls[side]]
        ikHandle = self.armIkCntrls[side] 
        ikPv = self.armPvCntrls[side]
    
        if self.fkikRadioBtn.isChecked():
            FKIK.snapFKtoIK(fkCntrls, ikJoints)
        else:
            FKIK.snapIKtoFK(fkCntrls, ikCntrls, ikHandle, ikPv, offset= 1)

    def snapLegFKIK(self, side):
        '''
        Calls the snap methods for the legs.
        '''
        fkCntrls = self.legFkCntrls[side]
        ikJoints = self.legIkChains[side]
        ikCntrls = [self.legStartCntrls[side], self.legStartCntrls[side]]
        ikHandle = self.legIkCntrls[side] 
        ikPv = self.legPvCntrls[side]
        
        if self.fkikRadioBtn.isChecked():
            FKIK.snapFKtoIK(fkCntrls, ikJoints)
        else:
            FKIK.snapIKtoFK(fkCntrls, ikCntrls, ikHandle, ikPv, offset=0)

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
            self.legChains = {} # using dict to separate the sides (_l, _r)
            self.legFkChains = {}
            self.legIkChains = {}
            self.legFkCntrls = {}
            self.legStartCntrls = {}
            self.legIkCntrls = {}
            self.legPvCntrls = {}
            self.legSwitches = {}
            
            if self.legsIkFkRadioBtn.isChecked():
                for side in ['_l', '_r']:
                    self.legChains[side] = ['thigh' + side, 'knee' + side, 'foot' + side]
                    
                    (self.legFkChains[side], 
                    self.legIkChains[side], 
                    self.legFkCntrls[side], 
                    self.legStartCntrls[side], 
                    self.legIkCntrls[side], 
                    self.legPvCntrls[side]) = FKIK.createFKIKAccessories(self.legChains[side], 'leg' + side, 
                                                                    controllerRadius=13, fkParent=self.rootControls[1], 
                                                                    ikParent=self.rootControls[0] + '_parent', 
                                                                    ikStartParent=self.rootControls[1])
                                                                        
                    self.legSwitches[side] = FKIK.createFKIKSwitch(self.legFkChains[side], self.legIkChains[side], 
                                                                self.legChains[side], self.legFkCntrls[side], 
                                                                self.legStartCntrls[side], self.legIkCntrls[side], 
                                                                self.legPvCntrls[side], 'leg' + side + '_switch')
                self.isLegFKIK = True

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
                
            # self.createFingerControllers('thumb', 'ctrl_arm') # spent so much time trying to get fingers to work only to know that it's not required
            # self.createFingerControllers('index', 'ctrl_arm')
            # self.createFingerControllers('middle', 'ctrl_arm')

        elif self.armsIkFkRadioBtn.isChecked(): # IK/FK
            self.armChains = {} # using dict to separate the sides (_l, _r)
            self.armFkChains = {}
            self.armIkChains = {}
            self.armFkCntrls = {}
            self.armStartCntrls = {}
            self.armIkCntrls = {}
            self.armPvCntrls = {}
            self.armSwitches = {}
            
            for side in ['_l', '_r']:
                self.armChains[side] = ['clavicle' + side, 'upperArm' + side, 'lowerArm' + side, 'hand' + side]
                
                (self.armFkChains[side], 
                self.armIkChains[side], 
                self.armFkCntrls[side], 
                self.armStartCntrls[side], 
                self.armIkCntrls[side], 
                self.armPvCntrls[side]) = FKIK.createFKIKAccessories(self.armChains[side], 'arm' + side, 
                                                                    controllerRadius=8, 
                                                                    fkParent=self.spineControls[-1], 
                                                                    ikParent=self.rootControls[0] + '_parent', 
                                                                    ikStartParent=self.spineControls[-1], 
                                                                    ikOffset=1)
                                                                    
                self.armSwitches[side] = FKIK.createFKIKSwitch(self.armFkChains[side], self.armIkChains[side], 
                                                            self.armChains[side], self.armFkCntrls[side], 
                                                            self.armStartCntrls[side], self.armIkCntrls[side], 
                                                            self.armPvCntrls[side], 'arm' + side + '_switch')
            self.isArmFKIK = True

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
        if self.splineSpine:
            self.spineControls = IK.createSplineSpineIK('spine1', 'spine4', 'spine9', name = 'spine_ik')
            cmds.parent(self.spineControls[-1], self.rootControls[-1])
        else: 
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

        cmds.delete('root_parentConstraint1', 'pelvis_parentConstraint1') # remove 90 degree rotation on ctrl_root_parent
        cmds.makeIdentity(self.rootControls[0] + '_parent', apply=True, t=1, r=1, s=1, n=0, pn=1)
        cmds.parentConstraint('ctrl_root', 'root', mo=True, name='root_parentConstraint1')
        cmds.parentConstraint('ctrl_pelvis', 'pelvis', mo=True, name='pelvis_parentConstraint1')

        self.scaleUniform = False

        if self.rootUniformScaleCheckbox.isChecked():
            self.scaleUniform = True

        self.rootGroupBox.setDisabled(True)
        self.spineGroupBox.setEnabled(True)

    def createUnifromScaling(self, rootCntrl, parentGrp):
        '''
        Scale the rig uniformly if we scale the root control.
        '''
        parentKids = cmds.listRelatives(parentGrp, children=True)
        parentKids.remove(rootCntrl + '_parent')

        for kid in parentKids: # Move everything under the root control to allow for uniform scaling
            print(kid)
            cmds.parent(kid, rootCntrl)
            
        rootCntrlKids = cmds.listRelatives(rootCntrl + '_parent', children=True)
        rootCntrlKids.remove(rootCntrl)

        for kid in rootCntrlKids:
            print(kid)
            cmds.parent(kid, rootCntrl)

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
                cmds.parent('leg_ik' + side, parentGrp)
            if cmds.objExists('arm_ik' + side):
                cmds.parent('arm_ik' + side, parentGrp)
            if cmds.objExists('leg' + side + '_ik'):
                cmds.parent('leg' + side + '_ik', parentGrp)
            if cmds.objExists('arm' + side + '_ik'):
                cmds.parent('arm' + side + '_ik', parentGrp)   
            if cmds.objExists('leg'+ side + '_switch'):
                cmds.parent('leg' + side + '_switch', parentGrp)
            if cmds.objExists('arm'+ side + '_switch'):
                cmds.parent('arm' + side + '_switch', parentGrp)

        if self.scaleUniform: # send everything under the root control to allow for uniform scaling
            self.createUnifromScaling(self.rootControls[0], parentGrp)

        # cmds.scaleConstraint(self.rootControls[0], parentGrp, maintainOffset=True) #uniform scaling
        # cmds.setAttr(self.rootControls[0] + '.inheritsTransform', 0)

        if self.isLegFKIK or self.isArmFKIK: # selectively enable the fkik snapping group box based on the rig created                 
            self.fkIkSnappingGroupBox.setEnabled(True)

            if self.isLegFKIK is False:
                self.lLegBtn.setDisabled(True)
                self.rLegBtn.setDisabled(True)
                
            if self.isArmFKIK is False:
                self.lArmBtn.setDisabled(True)
                self.rArmBtn.setDisabled(True)
        
    
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
    Creates FKIK switchs and controls for the arms and legs.
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

        return fkChain, ikChain, fkCntrls, startCntrl, ikCntrl, pvCntrl # keeping track of the controls and chains     
    
    @staticmethod
    def createFKIKSwitch(fkChain, ikChain, bindChain, fkCntrls, startCntrl, ikCntrl, pvCntrl, switchName):
        '''
        Creates the FKIK switch.
        '''
        switchCtrl = cmds.circle(n=switchName, nr=(0,0,1), c=(-20, 0, 0), r=5)[0]
        Helpers.changeControllerProperites(switchCtrl, color=17, width=2) # give it a distinct look

        cmds.delete(cmds.parentConstraint(bindChain[-1], switchCtrl))

        cmds.addAttr(switchCtrl, ln='FKIK_Switch', at='enum', en='fk:ik:', k=True) # using enums instead of bools :)

        for fk, ik, b in zip(fkChain, ikChain, bindChain):
            oc = cmds.orientConstraint(fk, ik, b, mo=True)[0]

            cmds.connectAttr(switchCtrl + '.FKIK_Switch', oc + '.w1')
            reverseNode = cmds.shadingNode('reverse', asUtility=True, n='reverse_' + b) # to get the opposite of the switch i.e fk
            cmds.connectAttr(switchCtrl + '.FKIK_Switch', reverseNode + '.inputX')
            cmds.connectAttr(reverseNode + '.outputX', oc + '.w0')

        reverseVis =  cmds.shadingNode('reverse', asUtility=True, n=switchName + '_reverseVis') # again to get the opposite of the switch i.e fk
        cmds.connectAttr(switchCtrl + '.FKIK_Switch', reverseVis + '.inputX')

        for fkCntrl in fkCntrls:
            cmds.connectAttr(reverseVis + '.outputX', fkCntrl + '.visibility')

        cmds.connectAttr(switchCtrl + '.FKIK_Switch', startCntrl + '.visibility', f=True)
        cmds.connectAttr(switchCtrl + '.FKIK_Switch', ikCntrl + '.visibility', f=True)
        cmds.connectAttr(switchCtrl + '.FKIK_Switch', pvCntrl + '.visibility', f=True)

        Helpers.lockAndHide(switchCtrl, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])   

        return switchCtrl
    
    @staticmethod
    def snapFKtoIK(fkControls, ikJoints):
        '''
        Snaps FK controls to match the pose of IK controls.
        '''
        for fk, ik in zip(fkControls, ikJoints): # match the pose of the fk controls to the ik joints
            for attr in['rx', 'ry', 'rz']:
                curr = cmds.getAttr(ik + '.' + attr)
                cmds.setAttr(fk + '.' + attr, curr)

    @staticmethod
    def snapIKtoFK(fkControls, ikControls, ikHandle, ikPv, offset = 0):
        '''
        Snaps IK controls to match the pose of FK controls.
        '''
        cmds.matchTransform(ikHandle, fkControls[-1], pos=True, rot=True)

        initPos = cmds.xform(fkControls[0 + offset], q=True, ws=True, t=True) # start of the fk chain
        midPos = cmds.xform(fkControls[1 + offset], q=True, ws=True, t=True) # mid of the fk chain (assuming 3 joints in the fk chain) (elbow or knee)
        finPos = cmds.xform(fkControls[-1], q=True, ws=True, t=True) # end of the fk chain
        meanPos = [(initPos[i] + finPos[i]) / 2 for i in range(3)] 
        
        dir = [midPos[i] - meanPos[i] for i in range(3)] # direction vector from the mid point to the mid joint
        pvPos = [midPos[i] + dir[i] * 2 for i in range(3)] # pole vector position (2x because it's a bit far from the mid joint)

        cmds.move(pvPos[0], pvPos[1], pvPos[2], ikPv)

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
        Helpers.changeControllerProperites(poleVector, color=13)

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
        Helpers.changeControllerProperites(controller, color=13)

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
        Helpers.changeControllerProperites(controller, color=13)

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
    
    @staticmethod
    def createSplineSpineIK(startJ, middleJ, endJ, name = 'spineIK'):
        '''
        Creates a spline IK for the spine.
        '''
        handle = cmds.ikHandle(n=name, sj=startJ, ee=endJ, sol='ikSplineSolver', ccv=True, pcv=False)
        handleCurve = cmds.rename(handle[2], name + '_curve')
        endEffector = cmds.rename(handle[1], name + '_effector')

        cmds.select(handleCurve + '.cv[0:1]', r=True)
        lowerCluster = cmds.cluster(n=name + '_lowerCluster')[1]
        cmds.select(handleCurve + '.cv[2:3]', r=True)
        upperCluster = cmds.cluster(n=name + '_upperCluster')[1]

        lowerCtrl = Helpers.makeCircleControls(startJ, name + '_lowerCtrl', 20) 
        upperCtrl = Helpers.makeCircleControls(endJ, name + '_upperCtrl', 20)
        bodyCtrl = Helpers.makeCircleControls(startJ, name + '_bodyCtrl', 25)
        middleCtrl = Helpers.makeCircleControls(middleJ, name + '_middleCtrl', 20)

        # for ctrl, cluster in zip([lowerCtrl, upperCtrl], [lowerCluster, upperCluster]):
        #     cmds.pointConstraint(cluster, ctrl, mo=False)
        #     cmds.delete(ctrl, cn=True)
        
        cmds.parent(upperCluster, upperCtrl)
        cmds.parent(lowerCluster, lowerCtrl)
        cmds.parent(lowerCtrl, bodyCtrl)
        cmds.parent(upperCtrl, middleCtrl)
        cmds.parent(middleCtrl, bodyCtrl)

        cmds.parentConstraint(lowerCtrl, startJ, mo=True)
        cmds.parentConstraint(upperCtrl, endJ, mo=True)

        splineGrp = cmds.group(handle[0], handleCurve, n=name + '_grp')
        cmds.parent(bodyCtrl, splineGrp)
        cmds.connectAttr(upperCtrl + '.rotateY', handle[0] + '.twist')

        return bodyCtrl, middleCtrl, lowerCtrl, upperCtrl, splineGrp

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
    def createSkeleton(markerData, splineSpine = False):
        '''
        Creates the skeleton from the given markers.
        '''
        if splineSpine:
            baseMarkers = [marker[0] for marker in Markers.defaultSplineBaseMarkers()]
        else:
            baseMarkers = [marker[0] for marker in Markers.defaultBaseMarkers()]

        leftSideMarkers = [marker[0] for marker in Markers.defaultLeftMarkers()]
        rightSideMarkers = [marker[0] for marker in Markers.defaultRightMarkers()]

        rootJ = Skeleton.createJointFromMarker('root', markerData) # base joints
        pelvisJ = Skeleton.createJointFromMarker('pelvis', markerData, jParent=rootJ)
        spineJs = Skeleton.createJointChainFromMarkers(baseMarkers[2:], markerData, jParent=pelvisJ)

        leftArmJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[:4], markerData, jParent=spineJs[-3]) # left joints
        leftThumbJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[4:7], markerData, jParent=leftArmJs[-1])
        leftIndexJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[7:10], markerData, jParent=leftArmJs[-1])
        leftMiddleJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[10:13], markerData, jParent=leftArmJs[-1])
        leftLegJs = Skeleton.createJointChainFromMarkers(leftSideMarkers[13:], markerData, jParent=pelvisJ)

        rightArmJs = Skeleton.createJointChainFromMarkers(rightSideMarkers[:4], markerData, jParent=spineJs[-3]) # right joints
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
    def defaultSplineBaseMarkers():
        '''
        Returns the base markers for the spline spine.
        '''
        return [
            ('root', (0, 0, 0)), ('pelvis', (0, 105, 0)), 
            ('spine1',(0, 111, 1.5)), ('spine2',(0, 117, 3)), ('spine3',(0, 125,5)),
            ('spine4',(0, 129, 4)), ('spine5',(0, 133,3)), ('spine6', (0, 138, 2.5)), 
            ('spine7',(0, 142, 0.5)),('spine8',(0, 146, -2)),('spine9', (0.0, 150, -4.5)),
            ('neck', (0, 158.5, -3)), ('head', (0, 181.5, 1))
        ]
    
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

    @staticmethod
    def changeControllerProperites(controller, color = None, width = None):
        '''
        Changes the properties of the given controller.
        '''
        controllerShape = cmds.listRelatives(controller, shapes=True)[0]
        cmds.setAttr(controllerShape + '.overrideEnabled', 1)
        
        if color:
            cmds.setAttr(controllerShape + '.overrideColor', color)
        if width:
            cmds.setAttr(controllerShape + '.lineWidth', width)

    @staticmethod
    def makeCircleControls(joint, ctrlName, radius):
        '''
        Creates a circle control for the given joint.
        '''
        cntrl = cmds.circle(n=ctrlName, nr=(0, 0, 1), c=(0, 0, 0), r=radius)[0]
        Helpers.changeControllerProperites(cntrl, color=13)

        cmds.pointConstraint(joint, cntrl)
        cmds.delete(cntrl, cn=True)

        cmds.rotate(90, 0, 0, cntrl)

        cmds.makeIdentity(cntrl, apply=True, r=True, s=True, t=True, n=False, pn=True)
        cmds.delete(cntrl, ch=True)

        return cntrl

arGUI = AutoRiggerGUI() # Create an instance of the AutoRiggerGUI class and show it
arGUI.show()