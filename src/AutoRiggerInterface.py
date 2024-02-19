'''
Instructions:
Keep the icons folder in the same directory as the script for the icons to be displayed in the visualizer widget.
Position the camera in the scene in the front of the model, to easily work with the visualizer widget. [Optional]
'''

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
       
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
        self.initLayout()
        self.initWidgets()

    def initWindow(self):
        self.setWindowTitle("Makra's Auto Rigger")
        screenSize = self.screen().size()
        self.setMinimumSize(screenSize.width()//3,screenSize.height()//2)

    def initWidgets(self):
        '''
        Initializes the widgets for all the different parts of the body.
        '''
        self.initVisualizer()
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

        self.visualizerLayout = QVBoxLayout()
        self.skeletonGuidesLayout = QVBoxLayout()
        self.visualizerLayout.addLayout(self.skeletonGuidesLayout)

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
        self.visualizer.addIcon(QPoint(60, 50), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/legL.png'), iconLabel= "Legs")
        self.visualizer.addIcon(QPoint(110, 50), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/legR.png'))
        self.visualizer.addIcon(QPoint(60, 100), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/armL.png'), iconLabel= "Arms")
        self.visualizer.addIcon(QPoint(110, 100), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/armR.png'))
        self.visualizer.addIcon(QPoint(60, 150), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/spine.png'), iconLabel= "Spine")
        self.visualizer.addIcon(QPoint(60, 200), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/head.png'), iconLabel= "Head")
        self.visualizer.addIcon(QPoint(60, 250), iconPath=os.path.join(parentDir, 'AutoRiggerIcons/root.png'), iconLabel= "Root")

        self.visualizer.showRig()

        self.createSkeletonGuidesBtn = QPushButton("Create Skeleton Guides")
               
        self.skeletonGuidesLayout.addWidget(self.createSkeletonGuidesBtn)        
        self.visualizerLayout.addWidget(self.visualizer) 

    def initLegsWidgets(self):
        '''
        Initializes the widgets required for the Legs section.
        It also creates a group box to contain the widgets and sets the layout for the group box.
        Finally, it adds the group box to the options layout.
        '''
        self.legsIkRadioBtn = QRadioButton("IK")
        self.legsFkRadioBtn = QRadioButton("FK")
        self.legsIkFkRadioBtn = QRadioButton("IK/FK")

        self.legsSpaceSwitchingCheckbox = QCheckBox("Space Switching")
        self.legsReverseFootIkCheckbox = QCheckBox("Reverse Foot IK")
        self.legsStretchyCheckbox = QCheckBox("Stretchy")

        self.legsCreateLegsJointsBtn = QPushButton("Create Joints")

        self.legsGroupBox = QGroupBox("LEGS")

        self.legsGroupBox.setLayout(self.createSectionLayout(
            [self.legsIkRadioBtn, self.legsFkRadioBtn, self.legsIkFkRadioBtn],
            [self.legsSpaceSwitchingCheckbox, self.legsReverseFootIkCheckbox, self.legsStretchyCheckbox],
            self.legsCreateLegsJointsBtn
        ))

        self.optionsLayout.addWidget(self.legsGroupBox)

    def initArmsWidgets(self):
        '''
        Initializes the widgets required for the Arms section.
        '''
        self.armsIkRadioBtn = QRadioButton("IK")
        self.armsFkRadioBtn = QRadioButton("FK")
        self.armsIkFkRadioBtn = QRadioButton("IK/FK")

        self.armsSpaceSwitchingCheckbox = QCheckBox("Space Switching")
        self.armsWristRollCheckbox = QCheckBox("Wrist Roll")
        self.armsStretchyCheckbox = QCheckBox("Stretchy")

        self.createArmsJointsBtn = QPushButton("Create Joints")

        self.armsGroupBox = QGroupBox("ARMS")

        self.armsGroupBox.setLayout(self.createSectionLayout(
            [self.armsIkRadioBtn, self.armsFkRadioBtn, self.armsIkFkRadioBtn],
            [self.armsSpaceSwitchingCheckbox, self.armsWristRollCheckbox, self.armsStretchyCheckbox],
            self.createArmsJointsBtn
        ))

        self.optionsLayout.addWidget(self.armsGroupBox)

    def initSpineWidgets(self):
        '''
        Initializes the widgets required for the Spine section.
        '''
        self.spineSpaceSwitchingCheckbox = QCheckBox("Space Switching")
        self.spineStretchyCheckbox = QCheckBox("Stretchy")

        self.createSpineJointsBtn = QPushButton("Create Joints")

        self.spineGroupBox = QGroupBox("SPINE")

        self.spineGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.spineSpaceSwitchingCheckbox, self.spineStretchyCheckbox],
            self.createSpineJointsBtn
        ))

        self.optionsLayout.addWidget(self.spineGroupBox)

    def initHeadWidgets(self):
        '''
        Initializes the widgets required for the Head section.
        '''
        self.headSpaceSwitchingCheckbox = QCheckBox("Space Switching")
        self.headStretchyCheckbox = QCheckBox("Stretchy")

        self.createHeadJointsBtn = QPushButton("Create Joints")

        self.headGroupBox = QGroupBox("HEAD")

        self.headGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.headSpaceSwitchingCheckbox, self.headStretchyCheckbox],
            self.createHeadJointsBtn
        ))

        self.optionsLayout.addWidget(self.headGroupBox)

    def initRootWidgets(self):
        '''
        Initializes the widgets required for the Root section.
        '''
        self.rootSpaceSwitchingCheckbox = QCheckBox("Space Switching")
        self.rootStretchyCheckbox = QCheckBox("Stretchy")
        self.rootUniformScaleCheckbox = QCheckBox("Uniform Scale")

        self.createRootJointsBtn = QPushButton("Create Joints")

        self.rootGroupBox = QGroupBox("ROOT")

        self.rootGroupBox.setLayout(self.createSectionLayout(
            [],
            [self.rootSpaceSwitchingCheckbox, self.rootStretchyCheckbox, self.rootUniformScaleCheckbox],
            self.createRootJointsBtn
        ))

        self.optionsLayout.addWidget(self.rootGroupBox)

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

arGUI = AutoRiggerGUI() # Create an instance of the AutoRiggerGUI class and show it
arGUI.show()