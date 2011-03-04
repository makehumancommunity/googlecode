import os.path
#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d
import mh
import os
import algos3d
import aljabr
import math
import poseengine
print 'Pose plugin imported'


class PoseTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Posing')      

        self.engine = poseengine.Poseengine(self.app.selectedHuman)        
        self.shoulder = self.engine.getLimb("joint-r-shoulder")
        self.shoulder.oBoundingBox = [[0.0, 8.1955895],[3.674790375, 6.1586085],[-1.120018, 1.192948875]]
        #self.shoulder.oBoundingBox = [[0.592449, 2.9099749999999998],\
        #[3.3710944999999994, 5.9782154999999992],\
        #[-1.2123235000000001, 0.79384575000000002]]
        
        self.shoulder.rotOrder = "xzy"
        
        self.shoulder.keyRot0 = [-90,90]
        self.shoulder.keyRot1 = [-135,-67,0,45]
        self.shoulder.keyRot2 = [-115,-90,-67,-45,-22,0,22,45,67,90]

        y = 80
        gui3d.GroupBox(self, [10, y, 9.0], 'Shoulder', gui3d.GroupBoxStyle._replace(height=25+36*3+4+24*3+6));y+=25

        self.shoulderXslider = gui3d.Slider(self, position=[10, y, 9.3], value = 0.0, min = -85, max = 80, label = "RotX: 0");y+=36
        self.shoulderYslider = gui3d.Slider(self, position=[10, y, 9.3], value = 0.0, min = -140, max = 50, label = "RotY: 0");y+=36
        self.shoulderZslider = gui3d.Slider(self, position=[10, y, 9.3], value = 0.0, min = -120, max = 90, label = "RotZ: 0");y+=36
        y+=4

        self.savePoseFiles = 0

        self.resetPoseButton = gui3d.Button(self, [18, y, 9.5], "Reset");y+=24
        self.testPoseButton = gui3d.Button(self, [18, y, 9.5], "Test");y+=24
        
        self.savePoseToggle = gui3d.CheckBox(self, [18, y, 9.5], "SavePose");y+=24

        @self.savePoseToggle.event
        def onClicked(event):
            gui3d.ToggleButton.onClicked(self.savePoseToggle, event)
            if self.savePoseToggle.selected:
                print "Save Pose activated"
            else:
                print "Save Pose deactivated"

        @self.testPoseButton.event
        def onClicked(event):
            self.test(self.shoulder)

        @self.resetPoseButton.event
        def onClicked(event):
            self.reset(self.shoulder)

        @self.shoulderXslider.event
        def onChange(value):            
            self.shoulder.angle[0] = value
            self.shoulder.applyPose()
            self.shoulderXslider.label.setText('RotX: %d' % value)
            
        @self.shoulderXslider.event
        def onChanging(value):            
            self.shoulderXslider.label.setText('RotX: %d' % value)
            
        @self.shoulderYslider.event
        def onChange(value):            
            self.shoulder.angle[1] = value 
            self.shoulder.applyPose()
            self.shoulderYslider.label.setText('RotY: %d' % value)
            
        @self.shoulderYslider.event
        def onChanging(value):            
            self.shoulderYslider.label.setText('RotY: %d' % value)

        @self.shoulderZslider.event
        def onChange(value):
            self.shoulder.angle[2] = value 
            self.shoulder.applyPose()
            self.shoulderZslider.label.setText('RotZ: %d' % value)
            
        @self.shoulderZslider.event
        def onChanging(value):            
            self.shoulderZslider.label.setText('RotZ: %d' % value)
            
    def onShow(self, event):
        self.app.selectedHuman.storeMesh()
        #self.applyPose()
        gui3d.TaskView.onShow(self, event)

    def onHide(self, event):
        self.app.selectedHuman.restoreMesh()
        self.app.selectedHuman.meshData.update()
        gui3d.TaskView.onHide(self, event)

    def test(self, limbToSave, sliderX,sliderY,sliderZ,savePose = None):

        homedir = os.path.expanduser('~')
        if self.savePoseToggle.selected:
            poseDir = os.path.join(homedir, limbToSave.name)
            if not os.path.isdir(poseDir):
                os.mkdir(poseDir)

        for angle in limbToSave.examplesTrasl:
            
            if self.savePoseToggle.selected:
                tName = "limb_%s_%s_%s.pose"%(angle[0],angle[1],angle[2])
                savePath = os.path.join(poseDir,tName)
                print "saved in %s"%(savePath)

            self.shoulderXslider.label.setText('RotX: %d'%(angle[0]))
            self.shoulderYslider.label.setText('RotY: %d'%(angle[1]))
            self.shoulderZslider.label.setText('RotZ: %d'%(angle[2]))
            self.shoulderXslider.setValue(angle[0])
            self.shoulderYslider.setValue(angle[1])
            self.shoulderYslider.setValue(angle[2])
            limbToSave.angle = angle
            limbToSave.applyPose(savePath)
            self.app.redraw()


    def reset(self, limbToTest):
        limbToTest.angle = [0,0,0]        
        self.shoulderXslider.label.setText('RotX: 0')
        self.shoulderYslider.label.setText('RotY: 0')
        self.shoulderZslider.label.setText('RotZ: 0')
        self.shoulderXslider.setValue(0.0)
        self.shoulderYslider.setValue(0.0)
        self.shoulderZslider.setValue(0.0)
        limbToTest.applyPose()
        self.app.redraw()
        

category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Experiments')
    taskview = PoseTaskView(category)
    print 'pose loaded'
            
    @taskview.event
    def onMouseDown(event):
        part = app.scene3d.getSelectedFacesGroup()
        print part.name

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    print 'pose unloaded'

