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

class SkeletonAction(gui3d.Action):
    def __init__(self, name, library, before, after):
        super(SkeletonAction, self).__init__(name)
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.chooseSkeleton(self.after)
        return True

    def undo(self):
        self.library.chooseSkeleton(self.before)
        return True

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

        self.humanChanged = False

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

        self.showWeightsTggl = displayBox.addWidget(gui.ToggleButton("Show bone weights"))
        @self.showWeightsTggl.mhEvent
        def onClicked(event):
            if self.showWeightsTggl.selected:
                # Highlight bone selected in bone explorer again
                for rdio in self.boneSelector:
                    if rdio.selected:
                        self.highlightBone(str(rdio.text()))
            else:
                self.clearBoneWeights()
        self.showWeightsTggl.setSelected(True)

        self.rigBox = self.addRightWidget(gui.GroupBox('Skeleton rig'))
        self.rigSelector = []

        self.boneBox = self.addLeftWidget(gui.GroupBox('Bones'))
        self.boneSelector = []

        self.infoBox = self.addRightWidget(gui.GroupBox('Rig info'))
        self.boneCountLbl = self.infoBox.addWidget(gui.TextView('Bones: '))
        self.descrLbl = self.infoBox.addWidget(gui.TextView('Description: '))

        self.rigDescriptions = { 
            "soft1":       "Soft skinned rig\nSimple version of the MHX\nreference rig containing\n only its deforming bones.",
            "xonotic":     "Rig compatible\nwith the open-source game\nXonotic.",
            "second_life": "Rig compatible\nwith Second Life.",
            "game":        "A simple rig\nwith a minimal amount of \nbones. Has limited\nexpressivity in hands\nand face.",
            "humanik":     "Rig compatible\nwith the HumanIK software.",
            "rigid":       "Same as soft1\na simple version of the MHX\nreference rig, but with\nrigid weighting.",
        }

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        self.oldHumanTransp = self.human.meshData.transparentPrimitives
        self.setHumanTransparency(True)
        self.human.meshData.setPickable(False)

        if not self.jointsObj:
            self.drawJointHelpers()

        self.reloadSkeletonChooser()

        # Rebuild skeleton if human has changed
        if self.human.skeleton and self.human.skeleton.dirty:
            # TODO have a more efficient way of adapting skeleton to new joint positions without re-reading rig files
            # TODO offer a skeleton getter that exporters can use that will rebuild the skeleton if it is dirty
            self.chooseSkeleton(self.human.skeleton.file)
            # Re-draw joints positions
            self.drawJointHelpers()
            self.human.skeleton.dirty = False
            self.humanChanged = False
        elif self.humanChanged:
            self.drawJointHelpers()
            self.humanChanged = False

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        self.setHumanTransparency(False)
        self.human.meshData.setPickable(True)
        self.removeBoneHighlights()

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
                        if self.human.skeleton:
                            oldSkelFile = self.human.skeleton.file
                        else:
                            oldSkelFile = None
                        gui3d.app.do(SkeletonAction("Change skeleton",
                                                    self,
                                                    oldSkelFile,
                                                    rdio.rigFile))

    def chooseSkeleton(self, filename):
        """
        Load skeleton from rig definition in a .rig file.
        """
        log.debug("Loading skeleton from rig file %s", filename)
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
            self.reloadBoneExplorer()
            self.boneCountLbl.setText("Bones: ")
            self.descrLbl.setText("Description: ")
            return

        self.human.skeleton, boneWeights = skeleton.loadRig(filename, self.human.meshData)
        # Store a reference to the currently loaded rig
        self.human.skeleton.file = filename
        self.human.skeleton.dirty = False   # Flag used for deferred updating

        # Created an AnimatedMesh object to manage the skeletal animation on the
        # human mesh and optionally additional meshes.
        # The animation manager object is accessible by other plugins via 
        # gui3d.app.currentHuman.animated.
        self.human.animated = animation.AnimatedMesh(self.human.skeleton, self.human.meshData, boneWeights)

        self.drawSkeleton(self.human.skeleton)

        self.reloadBoneExplorer()
        self.boneCountLbl.setText("Bones: %s" % self.human.skeleton.getBoneCount())
        if self.human.skeleton.name in self.rigDescriptions.keys():
            descr = self.rigDescriptions[self.human.skeleton.name]
        else:
            descr = "None available"
        self.descrLbl.setText("Description: %s" % descr)

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
            self.removeBoneHighlights()
            self.highlightBone(event.group.name)

        @self.skelObj.mhEvent
        def onMouseExited(event):
            """
            Event fired when mouse hovers off of a skeleton mesh facegroup
            """
            gui3d.TaskView.onMouseExited(self, event)
            self.removeBoneHighlights()

            # Highlight bone selected in bone explorer again
            for rdio in self.boneSelector:
                if rdio.selected:
                    self.clearBoneWeights()
                    self.highlightBone(str(rdio.text()))

    def highlightBone(self, name):
        # Highlight bones
        self.selectedBone = name
        setColorForFaceGroup(self.skelMesh, self.selectedBone, [216, 110, 39, 255])
        gui3d.app.statusPersist(name)

        # Draw bone weights
        if self.showWeightsTggl.selected:
            _, boneWeights = self.human.animated.getMesh(self.human.meshData.name)
            self.showBoneWeights(name, boneWeights)

        gui3d.app.redraw()

    def removeBoneHighlights(self):
        # Disable highlight on bone
        if self.selectedBone:
            setColorForFaceGroup(self.skelMesh, self.selectedBone, [255,255,255,255])
            gui3d.app.statusPersist('')

            self.clearBoneWeights()
            self.selectedBone = None

            gui3d.app.redraw()

    def drawJointHelpers(self):
        """
        Draw the joint helpers from the basemesh that define the default or
        reference rig.
        """
        if self.jointsObj:
            self.removeObject(self.jointsObj)
            self.jointsObj = None
            self.jointsMesh = None
            self.selectedJoint = None

        jointGroupNames = [group.name for group in self.human.meshData.faceGroups if group.name.startswith("joint-")]
        # TODO maybe define a getter for this list in the skeleton module
        jointPositions = []
        for groupName in jointGroupNames:
            jointPositions.append(skeleton.getHumanJointPosition(self.human.meshData, groupName))

        self.jointsMesh = skeleton_drawing.meshFromJoints(jointPositions, jointGroupNames)
        self.jointsMesh.priority = 100
        self.jointsMesh.setPickable(True)
        self.jointsObj = self.addObject( gui3d.Object(self.human.getPosition(), self.jointsMesh) )
        self.jointsObj.setRotation(self.human.getRotation())

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

    def showBoneWeights(self, boneName, boneWeights):
        mesh = self.human.meshData
        try:
            weights = np.asarray(boneWeights[boneName][1], dtype=np.float32)
            verts = boneWeights[boneName][0]
        except:
            return
        red = np.maximum(weights, 0)
        green = 1.0 - red
        blue = np.zeros_like(red)
        alpha = np.ones_like(red)
        color = np.array([red,green,blue,alpha]).T
        color = (color * 255.99).astype(np.uint8)
        mesh.color[verts,:] = color
        mesh.markCoords(verts, colr = True)
        mesh.sync_all()

    def clearBoneWeights(self):
        mesh = self.human.meshData
        mesh.color[...] = (255,255,255,255)
        mesh.markCoords(colr = True)
        mesh.sync_all()

    def reloadBoneExplorer(self):
        # Remove old radio buttons
        for radioBtn in self.boneSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.boneSelector = []

        if not self.human.skeleton:
            return

        for bone in self.human.skeleton.getBones():
            radioBtn = self.boneBox.addWidget(gui.RadioButton(self.boneSelector, bone.name))
            @radioBtn.mhEvent
            def onClicked(event):
                for rdio in self.boneSelector:
                    if rdio.selected:
                        self.removeBoneHighlights()
                        self.highlightBone(str(rdio.text()))

    def setHumanTransparency(self, enabled):
        if enabled:
            self.human.meshData.setTransparentPrimitives(len(self.human.meshData.fvert))
        else:
            self.human.meshData.setTransparentPrimitives(self.oldHumanTransp)

    def onHumanChanged(self, event):
        human = event.human
        # Set flag to do a deferred skeleton update in the future
        if human.skeleton:
            human.skeleton.dirty = True
        self.humanChanged = True    # Used for updating joints

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
