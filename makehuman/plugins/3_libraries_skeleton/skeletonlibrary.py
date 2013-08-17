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

Main skeleton tab
"""

import mh
import gui
import gui3d
import module3d
import log
from collections import OrderedDict
#import filechooser as fc

import skeleton
import skeleton_drawing
import animation
import armature

import numpy as np
import os

#------------------------------------------------------------------------------------------
#   class SkeletonAction
#------------------------------------------------------------------------------------------

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


def _getSkeleton(self):
    log.debug("Get skeleton %s %s" % (self, self._skeleton))
    if not self._skeleton:
        return None
    if self._skeleton.dirty:
        log.debug("Rebuilding skeleton.")
        # Rebuild skeleton (when human has changed)
        # Loads new skeleton, creates new skeleton mesh and new animatedMesh object (with up-to-date rest coords)
        self._skeleton._library.chooseSkeleton(self._skeleton.options)
        # TODO have a more efficient way of adapting skeleton to new joint positions without re-reading rig files
        # TODO Also, currently a tiny change in joints positions causes a new animatedMesh to be constructed, requiring all BVH motions to be reloaded (which is not necessary if the rig structure does not change). It should be enough to re-sync the rest coordinates in the animatedMesh and move the coord positions of the skeleton mesh.
        self._skeleton.dirty = False
    return self._skeleton


def _getVertexWeights(self):
    if not self.getSkeleton():
        return None
    if not self.animated:
        return None

    _, bodyWeights = self.animated.getMesh("base.obj")
    return bodyWeights


#------------------------------------------------------------------------------------------
#   class SkeletonLibrary
#------------------------------------------------------------------------------------------

class SkeletonLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Skeleton')
        self.debugLib = None
        self.amtOptions = armature.options.ArmatureOptions()
        self.optionsSelector = None

        self.systemRigs = mh.getSysDataPath('rigs')
        self.userRigs = os.path.join(mh.getPath(''), 'data', 'rigs')
        self.rigPaths = [self.userRigs, self.systemRigs]
        if not os.path.exists(self.userRigs):
            os.makedirs(self.userRigs)
        self.extension = "rig"

        self.human = gui3d.app.selectedHuman
        self.human._skeleton = None
        self.human.animated = None
        # Attach getter to human to access the skeleton, that takes care of deferred
        # updating when the skeleton should change
        import types
        self.human.getSkeleton = types.MethodType(_getSkeleton, self.human, self.human.__class__)
        self.human.getVertexWeights = types.MethodType(_getVertexWeights, self.human, self.human.__class__)

        self.oldSmoothValue = False

        self.humanChanged = False   # Used for determining when joints need to be redrawn

        self.skelMesh = None
        self.skelObj = None

        self.jointsMesh = None
        self.jointsObj = None

        self.selectedJoint = None

        self.oldHumanTransp = self.human.meshData.transparentPrimitives

        #
        #   Display box
        #

        self.displayBox = self.addLeftWidget(gui.GroupBox('Display'))
        self.showHumanTggl = self.displayBox.addWidget(gui.ToggleButton("Show human"))
        @self.showHumanTggl.mhEvent
        def onClicked(event):
            if self.showHumanTggl.selected:
                self.human.show()
            else:
                self.human.hide()
        self.showHumanTggl.setSelected(True)

        self.showJointsTggl = self.displayBox.addWidget(gui.ToggleButton("Show joints"))
        @self.showJointsTggl.mhEvent
        def onClicked(event):
            if not self.jointsObj:
                return
            if self.showJointsTggl.selected:
                self.jointsObj.show()
            else:
                self.jointsObj.hide()
        self.showJointsTggl.setSelected(True)


        #
        #   Preset box
        #

        self.presetBox = self.addRightWidget(gui.GroupBox('Rig Presets'))

        self.presetClearBtn = self.presetBox.addWidget(gui.Button("Clear"))
        @self.presetClearBtn.mhEvent
        def onClicked(event):
            self.amtOptions.reset(self.optionsSelector, useMuscles=False)
            self.descrLbl.setText("")
            self.updateSkeleton(useOptions=False)

        self.presetDefaultBtn = self.presetBox.addWidget(gui.Button("Default"))
        @self.presetDefaultBtn.mhEvent
        def onClicked(event):
            self.amtOptions.reset(self.optionsSelector, useMuscles=False)
            self.descrLbl.setText("Description: The default rig. Use this for weighting")
            self.updateSkeleton()

        self.presetMuscleBtn = self.presetBox.addWidget(gui.Button("Muscles"))
        @self.presetMuscleBtn.mhEvent
        def onClicked(event):
            self.amtOptions.reset(self.optionsSelector, useMuscles=True)
            self.descrLbl.setText("Description: The default rig with muscle bones. Use this for weighting muscles")
            self.updateSkeleton()

        self.presetGameBtn = self.presetBox.addWidget(gui.Button("Game"))
        @self.presetGameBtn.mhEvent
        def onClicked(event):
            descr = self.amtOptions.loadPreset("game", self.optionsSelector)
            self.descrLbl.setText("Description: %s" % descr)
            self.updateSkeleton()

        self.presetHumanIkBtn = self.presetBox.addWidget(gui.Button("HumanIK"))
        @self.presetHumanIkBtn.mhEvent
        def onClicked(event):
            descr = self.amtOptions.loadPreset("humanik", self.optionsSelector)
            self.descrLbl.setText("Description: %s" % descr)
            self.updateSkeleton()

        self.presetSecondLifeBtn = self.presetBox.addWidget(gui.Button("Second Life"))
        @self.presetSecondLifeBtn.mhEvent
        def onClicked(event):
            descr = self.amtOptions.loadPreset("second_life", self.optionsSelector)
            self.descrLbl.setText("Description: %s" % descr)
            self.updateSkeleton()

        self.presetXonoticBtn = self.presetBox.addWidget(gui.Button("Xonotic"))
        @self.presetXonoticBtn.mhEvent
        def onClicked(event):
            descr = self.amtOptions.loadPreset("xonotic", self.optionsSelector)
            self.descrLbl.setText("Description: %s" % descr)
            self.updateSkeleton()

        self.infoBox = self.addLeftWidget(gui.GroupBox('Rig info'))
        self.boneCountLbl = self.infoBox.addWidget(gui.TextView('Bones: '))
        self.descrLbl = self.infoBox.addWidget(gui.TextView('Description: '))
        self.descrLbl.setSizePolicy(gui.QtGui.QSizePolicy.Ignored, gui.QtGui.QSizePolicy.Preferred)
        self.descrLbl.setWordWrap(True)


    def updateSkeleton(self, useOptions=True):
        if self.human.getSkeleton():
            oldSkelOptions = self.human.getSkeleton().options
        else:
            oldSkelOptions = None
        self.amtOptions.fromSelector(self.optionsSelector)
        if useOptions:
            string = "Change skeleton"
            options = self.amtOptions
        else:
            string = "Clear skeleton"
            options = None
        gui3d.app.do(SkeletonAction(string, self, oldSkelOptions, options))


    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setGlobalCamera()

        # Disable smoothing in skeleton library
        self.oldSmoothValue = self.human.isSubdivided()
        self.human.setSubdivided(False)

        self.oldHumanTransp = self.human.meshData.transparentPrimitives
        self.setHumanTransparency(True)
        self.human.meshData.setPickable(False)
        mh.updatePickingBuffer()

        if self.skelObj:
            self.skelObj.show()

        if not self.jointsObj:
            self.drawJointHelpers()

        #self.filechooser.refresh()

        # Make sure skeleton is updated when human has changed
        self.human.getSkeleton()

        # Re-draw joints positions if human has changed
        if self.humanChanged:
            self.drawJointHelpers()
            self.humanChanged = False


    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        if self.skelObj:
            self.skelObj.hide()
        self.setHumanTransparency(False)
        self.human.meshData.setPickable(True)
        mh.updatePickingBuffer()
        try:
            self.removeBoneHighlights()
        except:
            pass

        # Reset smooth setting
        self.human.setSubdivided(self.oldSmoothValue)


    def chooseSkeleton(self, options):
        """
        Load skeleton from an options set.
        """
        log.debug("Loading skeleton with options %s", options)

        try:
            self.removeBoneHighlights()
        except:
            pass

        if not options:
            # Unload current skeleton
            self.human._skeleton = None
            self.human.animated = None
            if self.skelObj:
                # Remove old skeleton mesh
                gui3d.app.removeObject(self.skelObj)
                self.skelObj = None
                self.skelMesh = None
            self.boneCountLbl.setText("Bones: ")
            #self.selectedBone = None

            if self.debugLib:
                self.debugLib.reloadBoneExplorer()
            return

        # Load skeleton definition from options
        self.human._skeleton, boneWeights = skeleton.loadRig(options, self.human.meshData)

        # Store a reference to the currently loaded rig
        self.human._skeleton.options = options
        self.human._skeleton.dirty = False   # Flag used for deferred updating
        self.human._skeleton._library = self  # Temporary member, used for rebuilding skeleton

        #self.filechooser.selectItem(options)

        # Created an AnimatedMesh object to manage the skeletal animation on the
        # human mesh and optionally additional meshes.
        # The animation manager object is accessible by other plugins via
        # gui3d.app.currentHuman.animated.
        self.human.animated = animation.AnimatedMesh(self.human.getSkeleton(), self.human.meshData, boneWeights)

        # (Re-)draw the skeleton
        skel = self.human.getSkeleton()
        self.drawSkeleton(skel)

        if self.debugLib:
            self.debugLib.reloadBoneExplorer()
            self.boneCountLbl.setText("Bones: %s" % self.human.getSkeleton().getBoneCount())


    def drawSkeleton(self, skel):
        if self.skelObj:
            # Remove old skeleton mesh
            gui3d.app.removeObject(self.skelObj)
            self.skelObj = None
            self.skelMesh = None
            self.selectedBone = None

        # Create a mesh from the skeleton in rest pose
        skel.setToRestPose() # Make sure skeleton is in rest pose when constructing the skeleton mesh
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
        self.skelMesh.priority = 100
        self.skelMesh.setPickable(True)
        mh.updatePickingBuffer()
        self.skelObj = gui3d.app.addObject(gui3d.Object(self.human.getPosition(), self.skelMesh) )
        self.skelObj.setRotation(self.human.getRotation())

        # Add the skeleton mesh to the human AnimatedMesh so it animates together with the skeleton
        # The skeleton mesh is supposed to be constructed from the skeleton in rest and receives
        # rigid vertex-bone weights (for each vertex exactly one weight of 1 to one bone)
        mapping = skeleton_drawing.getVertBoneMapping(skel, self.skelMesh)
        self.human.animated.addMesh(self.skelMesh, mapping)

        # Store a reference to the skeleton mesh object for other plugins
        self.human._skeleton.object = self.skelObj


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
        mh.updatePickingBuffer()
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


    def highlightBone(self, name):
        if self.debugLib is None:
            return

        # Highlight bones
        self.selectedBone = name
        setColorForFaceGroup(self.skelMesh, self.selectedBone, [216, 110, 39, 255])
        gui3d.app.statusPersist(name)

        # Draw bone weights
        if self.showWeightsTggl.selected:
            boneWeights = self.human.getVertexWeights()
            self.showBoneWeights(name, boneWeights)

        gui3d.app.redraw()


    def removeBoneHighlights(self):
        if self.debugLib is None:
            return

        # Disable highlight on bone
        if self.selectedBone:
            setColorForFaceGroup(self.skelMesh, self.selectedBone, [255,255,255,255])
            gui3d.app.statusPersist('')

            self.clearBoneWeights()
            self.selectedBone = None

            gui3d.app.redraw()


    def clearBoneWeights(self):
        mesh = self.human.meshData
        mesh.color[...] = (255,255,255,255)
        mesh.markCoords(colr = True)
        mesh.sync_all()


    def setHumanTransparency(self, enabled):
        if enabled:
            self.human.meshData.setTransparentPrimitives(len(self.human.meshData.fvert))
        else:
            self.human.meshData.setTransparentPrimitives(self.oldHumanTransp)


    def onHumanChanged(self, event):
        human = event.human
        # Set flag to do a deferred skeleton update in the future
        if human._skeleton:
            human._skeleton.dirty = True
        self.humanChanged = True    # Used for updating joints


    def onHumanChanging(self, event):
        human = event.human
        if event.change == 'reset':
            self.chooseSkeleton(None)


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
        if values[0] == "skeleton":
            skelFile = values[1]
            for path in self.rigPaths:
                skelPath = os.path.join(path, skelFile)
                if os.path.isfile(skelPath):
                    self.chooseSkeleton(skelPath)
                    return
            log.warn("Could not load rig %s, file does not exist." % skelFile)

        # Make sure no skeleton is drawn
        if self.skelObj:
            self.skelObj.hide()

    def saveHandler(self, human, file):
        if human.getSkeleton():
            file.write('skeleton %s ' % human.getSkeleton().options)



def setColorForFaceGroup(mesh, fgName, color):
    color = np.asarray(color, dtype=np.uint8)
    mesh.color[mesh.getVerticesForGroups([fgName])] = color[None,:]
    mesh.markCoords(colr=True)
    mesh.sync_color()
