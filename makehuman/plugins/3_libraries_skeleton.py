#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Skeleton library.
Allows a selection of skeletons which can be exported with the MH character.
Skeletons are used for skeletal animation (skinning) and posing.
"""

import gui3d
import mh
import gui
import module3d
import log

import skeleton
import skeleton_drawing
import animation

import numpy as np
import os

# TODO add bone explorer with weight highlighting on human mesh
class SkeletonLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Skeleton')

        self.systemRigs = os.path.join('data', 'rigs')
        self.userRigs = os.path.join(mh.getPath(''), 'data', 'rigs')
        self.rigPaths = [self.userRigs, self.systemRigs]
        self.extension = "rig"

        self.human = gui3d.app.selectedHuman
        self.human.skeleton = None
        self.human.animated = None

        self.skelMesh = None
        self.skelObj = None

        self.jointsMesh = None
        self.jointsObj = None

        self.selectedBone = None
        self.selectedJoint = None

        self.oldHumanTransp = self.human.meshData.transparentPrimitives

        displayBox = self.addLeftWidget(gui.GroupBox('Display'))
        self.showHumanTggl = displayBox.addWidget(gui.ToggleButton("Show human"))
        @self.showHumanTggl.mhEvent
        def onClicked(event):
            if self.showHumanTggl.selected:
                self.human.show()
            else:
                self.human.hide()
        self.showHumanTggl.setSelected(True)

        self.showJointsTggl = displayBox.addWidget(gui.ToggleButton("Show joints"))
        @self.showJointsTggl.mhEvent
        def onClicked(event):
            if not self.jointsObj:
                return
            if self.showJointsTggl.selected:
                self.jointsObj.show()
            else:
                self.jointsObj.hide()
        self.showJointsTggl.setSelected(True)

        self.rigBox = self.addRightWidget(gui.GroupBox('Skeleton rig'))
        self.rigSelector = []

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        self.oldHumanTransp = self.human.meshData.transparentPrimitives
        self.setHumanTransparency(True)

        if not self.jointsObj:
            self.drawJointHelpers()

        self.reloadSkeletonChooser()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        self.setHumanTransparency(False)

    def reloadSkeletonChooser(self):
        # Remove old radio buttons
        for radioBtn in self.rigSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.rigSelector = []

        # Retrieve all .rig files
        files = searchFiles(self.rigPaths, [self.extension])

        radioBtn = self.rigBox.addWidget(gui.RadioButton(self.rigSelector, "No skeleton", selected=not self.human.skeleton))
        radioBtn.rigFile = None
        for rigFile in files:
            rigName = os.path.splitext(os.path.basename(rigFile))[0]
            active = bool(self.human.skeleton and self.human.skeleton.file == rigFile)
            radioBtn = self.rigBox.addWidget(gui.RadioButton(self.rigSelector, rigName, selected=active))
            radioBtn.rigFile = rigFile

        for radioBtn in self.rigSelector:
            @radioBtn.mhEvent
            def onClicked(event):
                for rdio in self.rigSelector:
                    if rdio.selected:
                        self.chooseSkeleton(rdio.rigFile)

    def chooseSkeleton(self, filename):
        """
        Load skeleton from rig definition in a .rig file.
        """
        if not filename:
            # Unload current skeleton
            self.human.skeleton = None
            self.human.animated = None
            if self.skelObj:
                # Remove old skeleton mesh
                self.removeObject(self.skelObj)
                self.skelObj = None
                self.skelMesh = None
            self.selectedBone = None
            return

        self.human.skeleton, boneWeights = skeleton.loadRig(filename, self.human.meshData)
        # Store a reference to the currently loaded rig
        self.human.skeleton.file = filename

        # Created an AnimatedMesh object to manage the skeletal animation on the
        # human mesh and optionally additional meshes.
        # The animation manager object is accessible by other plugins via 
        # gui3d.app.currentHuman.animated.
        self.human.animated = animation.AnimatedMesh(self.human.skeleton, self.human.meshData, boneWeights)

        self.drawSkeleton(self.human.skeleton)

    def drawSkeleton(self, skel):
        if self.skelObj:
            # Remove old skeleton mesh
            self.removeObject(self.skelObj)
            self.skelObj = None
            self.skelMesh = None
            self.selectedBone = None

        # Create a mesh from the skeleton in rest pose
        skel.setToRestPose() # Make sure skeleton is in rest pose when constructing the skeleton mesh
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
        self.skelMesh.priority = 100
        self.skelMesh.setPickable(True)
        self.skelObj = self.addObject(gui3d.Object(self.human.getPosition(), self.skelMesh) )
        self.skelObj.setRotation(self.human.getRotation())

        # Add the skeleton mesh to the human AnimatedMesh so it animates together with the skeleton
        # The skeleton mesh is supposed to be constructed from the skeleton in rest and receives
        # rigid vertex-bone weights (for each vertex exactly one weight of 1 to one bone)
        mapping = skeleton_drawing.getVertBoneMapping(skel, self.skelMesh)
        self.human.animated.addMesh(self.skelMesh, mapping)

        # Add event listeners to skeleton mesh for bone highlighting
        @self.skelObj.mhEvent
        def onMouseEntered(event):
            """
            Event fired when mouse hovers over a skeleton mesh facegroup
            """
            gui3d.TaskView.onMouseEntered(self, event)

            # Highlight bones
            self.selectedBone = event.group
            setColorForFaceGroup(self.skelMesh, self.selectedBone.name, [216, 110, 39, 255])
            gui3d.app.statusPersist(event.group.name)
            gui3d.app.redraw()

        @self.skelObj.mhEvent
        def onMouseExited(event):
            """
            Event fired when mouse hovers off of a skeleton mesh facegroup
            """
            gui3d.TaskView.onMouseExited(self, event)
            
            # Disable highlight on bone
            if self.selectedBone:
                setColorForFaceGroup(self.skelMesh, self.selectedBone.name, [255,255,255,255])
                gui3d.app.statusPersist('')
                gui3d.app.redraw()

    def drawJointHelpers(self):
        """
        Draw the joint helpers from the basemesh that define the default or
        reference rig.
        """
        jointGroupNames = [group.name for group in self.human.meshData.faceGroups if group.name.startswith("joint-")]
        # TODO maybe define a getter for this list in the skeleton module
        jointPositions = []
        for groupName in jointGroupNames:
            jointPositions.append(skeleton.getHumanJointPosition(self.human.meshData, groupName))

        self.jointsMesh = skeleton_drawing.meshFromJoints(jointPositions, jointGroupNames)
        self.jointsMesh.priority = 100
        self.jointsMesh.setPickable(True)
        self.jointsObj = self.addObject( gui3d.Object(self.human.getPosition(), self.jointsMesh) )

        color = np.asarray([255, 255, 0, 255], dtype=np.uint8)
        self.jointsMesh.color[:] = color[None,:]
        self.jointsMesh.markCoords(colr=True)
        self.jointsMesh.sync_color()

        # Add event listeners to joint mesh for joint highlighting
        @self.jointsObj.mhEvent
        def onMouseEntered(event):
            """
            Event fired when mouse hovers over a joint mesh facegroup
            """
            gui3d.TaskView.onMouseEntered(self, event)

            # Highlight joint
            self.selectedJoint = event.group
            setColorForFaceGroup(self.jointsMesh, self.selectedJoint.name, [216, 110, 39, 255])
            gui3d.app.statusPersist(event.group.name)
            gui3d.app.redraw()

        @self.jointsObj.mhEvent
        def onMouseExited(event):
            """
            Event fired when mouse hovers off of a joint mesh facegroup
            """
            gui3d.TaskView.onMouseExited(self, event)
            
            # Disable highlight on joint
            if self.selectedJoint:
                setColorForFaceGroup(self.jointsMesh, self.selectedJoint.name, [255,255,0,255])
                gui3d.app.statusPersist('')
                gui3d.app.redraw()

    def setHumanTransparency(self, enabled):
        if enabled:
            self.human.meshData.setTransparentPrimitives(len(self.human.meshData.fvert))
        else:
            # TODO not working...
            self.human.meshData.setTransparentPrimitives(self.oldHumanTransp)

    def onHumanRotated(self, event):
        if self.skelObj:
            self.skelObj.setRotation(gui3d.app.selectedHuman.getRotation())
        if self.jointsObj:
            self.jointsObj.setRotation(gui3d.app.selectedHuman.getRotation())

    def onHumanTranslated(self, event):
        if self.skelObj:
            self.skelObj.setPosition(gui3d.app.selectedHuman.getPosition())
        if self.jointsObj:
            self.jointsObj.setPosition(gui3d.app.selectedHuman.getPosition())

    def loadHandler(self, human, values):
        pass
        
    def saveHandler(self, human, file):
        pass


def load(app):
    category = app.getCategory('Library')
    taskview = category.addTask(SkeletonLibrary(category))

    human = gui3d.app.selectedHuman
    app.addLoadHandler('skeleton', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements
def unload(app):
    pass


def setColorForFaceGroup(mesh, fgName, color):
    color = np.asarray(color, dtype=np.uint8)
    mesh.color[mesh.getVerticesForGroups([fgName])] = color[None,:]
    mesh.markCoords(colr=True)
    mesh.sync_color()

def searchFiles(paths, extensions):
    # TODO move this method somewhere to a shared module?
    for path in paths:
        for root, dirs, files in os.walk(path):
            for f in files:
                ext = os.path.splitext(f)[1][1:].lower()
                if ext in extensions:
                    if f.lower().endswith('.' + ext):
                        yield os.path.join(root, f)

