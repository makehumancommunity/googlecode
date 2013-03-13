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

Animation library.
A library of sets of animations to choose from that can be exported alongside
a MH model.
"""

import gui3d
import mh
import gui
import module3d
import log

import os
import numpy as np

import bvh
import skeleton
import skeleton_drawing
import animation

class AnimationLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Animations')

        # Test config param
        self.perFramePlayback = False   # Set to false to use time for playback

        self.interpolate = True     # Only useful when using time for playback

        self.skelMesh = None
        self.skelObj = None

        self.jointsMesh = None
        self.jointsObj = None

        self.bvhRig = None
        self.animations = []
        self.anim = None
        self.animatedMesh = None

        self.human = gui3d.app.selectedHuman
        self.oldHumanTransp = self.human.meshData.transparentPrimitives

        self.selectedBone = None

        self.timer = None
        self.currFrame = 0

        displayBox = self.addLeftWidget(gui.GroupBox('Display'))
        self.playbackBox = None
        self.frameSlider = None
        self.playPauseBtn = None
        self.animateInPlaceTggl = None

        self.showHumanTggl = displayBox.addWidget(gui.ToggleButton("Show human"))
        @self.showHumanTggl.mhEvent
        def onClicked(event):
            if self.showHumanTggl.selected:
                self.human.show()
            else:
                self.human.hide()
        self.showHumanTggl.setSelected(True)

        self.showSkeletonTggl = displayBox.addWidget(gui.ToggleButton("Show skeleton"))
        @self.showSkeletonTggl.mhEvent
        def onClicked(event):
            if not self.skelObj:
                return
            if self.showSkeletonTggl.selected:
                self.skelObj.show()
            else:
                self.skelObj.hide()
        self.showSkeletonTggl.setSelected(True)

        self.animationSelector = []
        self.animationsBox = self.addLeftWidget(gui.GroupBox('Animations'))

    def loadPose(self, filename, scale = 1.0, swapYZ = False):
        '''
        ## Old method #########################
        import armature

        amt = human.armature
        if not amt:
            # TODO createRig() does much much more than you would expect
            amt = human.armature = armature.rigdefs.createPoseRig(human, "soft1")            
        #amt.setModifier(modifier)
        #amt.readMhpFile(filepath)
        amt.readBvhFile(filename)
        #amt.listPose()
        #######################################
        '''
        print "Loading %s" % filename

        # Load BVH data
        bvhRig = bvh.load(filename, swapYZ)
        if scale != 1.0:
            # Scale rig
            bvhRig.scale(scale)      # TODO automatically rescale based on upper leg and fallback on bounding box

        if self.animateInPlaceTggl:
            inPlace = self.animateInPlaceTggl.selected
        else:
            inPlace = True
        self.animatedMesh.setAnimateInPlace(inPlace)

        # Load animation data from BVH file and add it to AnimatedMesh (if not added yet)
        name = os.path.splitext(os.path.basename(filename))[0]
        if not self.animatedMesh.hasAnimation(name):
            jointToBoneMap = [bone.name for bone in self.skeleton.getBones()] # This is a list that references a joint name in the BVH for each bone in the skeleton (breadth-first order)
            anim = bvhRig.createAnimationTrack(jointToBoneMap, name)
            # Sparsify data to test out interpolation
            print "sparsifying anim with framerate %s to %s" % (anim.frameRate, anim.frameRate/10)
            anim.sparsify(anim.frameRate/20)
            anim.interpolationType = 1 if self.interpolate else 0
            self.addAnimation(anim)

        # Create playback controls
        if not self.playbackBox:
            self.createPlaybackControl()

    def addAnimation(self, anim):
        log.debug("Frames: %s", anim.nFrames)
        log.debug("Playtime: %s", anim.getPlaytime())

        self.animations.append(anim.name)

        self.animatedMesh.addAnimation(anim)
        if len(self.animations) == 1:
            self.selectAnimation(anim.name)

        radioBtn = self.animationsBox.addWidget(gui.RadioButton(self.animationSelector, anim.name, selected=len(self.animationSelector) == 0))

        @radioBtn.mhEvent
        def onClicked(event):
            for rdio in self.animationSelector:
                if rdio.selected:
                    self.selectAnimation(str(rdio.text()))

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        self.oldHumanTransp = self.human.meshData.transparentPrimitives
        self.setHumanTransparency(True)
        self.human.meshData.setPickable(False)

        # Unload previously loaded animations
        self.animations = []
        for radioBtn in self.animationSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.animationSelector = []
        self.anim = None
        if self.human.animated:
            self.human.animated.removeAnimations()
        self.animatedMesh = None

        # Remove old rig
        if self.skelObj:
            self.removeObject(self.skelObj)
            if self.human.animated:
                self.human.animated.removeMesh(self.skelMesh)
            self.skelObj = None
            self.skelMesh = None
            self.selectedBone = None

        if self.human.skeleton:
            self.skeleton = self.human.skeleton

            self.drawSkeleton()

            if self.human.skeleton.name == "soft1":
                # Load a test pose for the soft1 rig
                path = os.path.join('data', 'poses', 'dance1')
                filename = os.path.join(path, 'dance1.bvh')
                self.loadPose(filename, 1.0, True)
                gui3d.app.statusPersist("Loaded dance1 pose one soft1 rig.")
            else:
                gui3d.app.statusPersist('No animations to load for the skeleton "%s". Try with no skeleton or soft1 rig.' % self.human.skeleton.name)
        else:
            # Load skeleton from BVH file
            # Load joint rig definition from BVH as skeleton
            # Convert joint rig and animation to a bone-based skeleton
            path = os.path.join('data', 'bvhs')
            filename = os.path.join(path, '02_02.bvh')
            bvhRig = bvh.load(filename, False)
            bvhRig.scale(0.1)
            self.skeleton = bvhRig.createSkeleton(False, None)

            self.drawSkeleton()

            # Test with loading a rig from BVH
            path = os.path.join('data', 'bvhs')
            filename = os.path.join(path, '02_02.bvh')
            self.loadPose(filename, 0.1, False)
            filename = os.path.join(path, '03_03.bvh')
            self.loadPose(filename, 0.1, False)
            gui3d.app.statusPersist("Loaded a rig and animations from BVH files.")

            '''
            # CMU
            path = os.path.join('data', 'bvhs/cmu')
            filename = os.path.join(path, '12_01.bvh')
            self.loadPose(filename)
            filename = os.path.join(path, '12_02.bvh')
            self.loadPose(filename)
            filename = os.path.join(path, '12_03.bvh')
            self.loadPose(filename)
            filename = os.path.join(path, '12_04.bvh')
            #self.loadPose(filename)
            '''

        self.frameSlider.setValue(0)

    def drawSkeleton(self):
        # Create a mesh from the skeleton in rest pose
        self.skelMesh = skeleton_drawing.meshFromSkeleton(self.skeleton, "Prism")
        self.skelMesh.priority = 100
        self.skelMesh.setPickable(True)
        self.skelObj = self.addObject( gui3d.Object(self.human.getPosition(), self.skelMesh) )
        self.skelObj.setRotation(self.human.getRotation())

        if self.showSkeletonTggl.selected:
            self.skelObj.show()
        else:
            self.skelObj.hide()

        if self.animateInPlaceTggl:
            inPlace = self.animateInPlaceTggl.selected
        else:
            inPlace = True
        mapping = skeleton_drawing.getVertBoneMapping(self.skeleton, self.skelMesh)
        if self.human.animated:
            # Add created skeleton to animatedMesh object associated with human.skeleton
            self.animatedMesh = self.human.animated
            self.animatedMesh.setAnimateInPlace(inPlace)
            self.animatedMesh.addMesh(self.skelMesh, mapping)
        else:
            # Create an animateable mesh object to animate the skeleton mesh
            self.animatedMesh = animation.AnimatedMesh(self.skeleton, self.skelMesh, mapping)
            self.animatedMesh.setAnimateInPlace(inPlace)

            # TODO we can skin the human model too if we retarget the BVH animation on a skeleton from the skeleton library (which define bone-to-vertex weights for the human)
            #self.animatedMesh.addMesh(self.human.meshData, mapping)

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

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        self.setToRestPose()
        self.setHumanTransparency(False)
        self.human.meshData.setPickable(True)

    def createPlaybackControl(self):
        self.playbackBox = self.addRightWidget(gui.GroupBox('Playback'))
        maxFrame = self.anim.nFrames-1
        if maxFrame < 1:
            maxFrame = 1
            # TODO disable slider
        self.frameSlider = self.playbackBox.addWidget(gui.Slider(value = 0, min = 0, max = maxFrame, label = 'Frame: %d'))
        # TODO make slider use time instead of frames?
        @self.frameSlider.mhEvent
        def onChanging(value):
            self.updateAnimation(value)
        @self.frameSlider.mhEvent
        def onChange(value):
            self.updateAnimation(value)

        self.playPauseBtn = self.playbackBox.addWidget(gui.Button("Play"))
        @self.playPauseBtn.mhEvent
        def onClicked(value):
            if self.playPauseBtn.text() == 'Play':
                self.startPlayback()
            else:
                self.stopPlayback()

        self.animateInPlaceTggl = self.playbackBox.addWidget(gui.ToggleButton("In-place animation"))
        @self.animateInPlaceTggl.mhEvent
        def onClicked(event):
            self.animatedMesh.setAnimateInPlace(self.animateInPlaceTggl.selected)
            self.updateAnimation(self.currFrame)
        self.animateInPlaceTggl.setSelected(True)

        self.restPoseBtn = self.playbackBox.addWidget(gui.Button("Set to Rest Pose"))
        @self.restPoseBtn.mhEvent
        def onClicked(value):
            self.setToRestPose()

        self.interpolateTggl = self.playbackBox.addWidget(gui.ToggleButton("Interpolate animation"))
        @self.interpolateTggl.mhEvent
        def onClicked(event):
            self.interpolate = self.interpolateTggl.selected
        self.interpolateTggl.setSelected(True)

    def startPlayback(self):
        self.playPauseBtn.setText('Pause')
        if self.perFramePlayback:
            self.timer = mh.addTimer(max(30, int(1.0/self.anim.frameRate * 1000)), self.onFrameChanged)
        else: # 30 FPS fixed
            self.timer = mh.addTimer(30, self.onFrameChanged)

    def stopPlayback(self):
        if not self.playPauseBtn:
            return
        self.playPauseBtn.setText('Play')
        if self.timer:
            mh.removeTimer(self.timer)
            self.timer = None

    def setToRestPose(self):
        # TODO have a one-method reset-to-rest on AnimatedMesh?
        self.animatedMesh.setActiveAnimation(None)
        self.animatedMesh.resetTime()
        self.stopPlayback()

    def selectAnimation(self, animName):
        self.stopPlayback()
        self.animatedMesh.setActiveAnimation(animName)
        self.anim = self.animatedMesh.getAnimation(animName)
        print "Setting animation to %s" % animName
        if self.frameSlider:
            self.frameSlider.setMin(0)
            maxFrame = self.anim.nFrames-1
            if maxFrame < 1:
                maxFrame = 1
                # TODO disable slider
            self.frameSlider.setMax(maxFrame)
            self.currFrame = 0
            self.frameSlider.setValue(0)
        self.updateAnimation(0)
        gui3d.app.redraw()

    def onFrameChanged(self):
        if not self.anim:
            return
        if self.perFramePlayback:
            frame = self.currFrame + 1
            if frame > self.frameSlider.max:
                frame = 0

            self.frameSlider.setValue(frame)
            self.updateAnimation(frame)
        else:
            self.animatedMesh.setActiveAnimation(self.anim.name)
            self.anim.interpolationType = 1 if self.interpolate else 0
            self.animatedMesh.update(1.0/30.0)
            frame = self.anim.getFrameIndexAtTime(self.animatedMesh.getTime())[0]
            self.frameSlider.setValue(frame)
        gui3d.app.redraw()

    def updateAnimation(self, frame):
        if not self.anim:
            return
        self.currFrame = frame
        self.animatedMesh.setActiveAnimation(self.anim.name)
        self.anim.interpolationType = 1 if self.interpolate else 0
        self.animatedMesh.setToFrame(frame)

    def setHumanTransparency(self, enabled):
        if enabled:
            self.human.meshData.setTransparentPrimitives(len(self.human.meshData.fvert))
        else:
            self.human.meshData.setTransparentPrimitives(self.oldHumanTransp)

    def loadHandler(self, human, values):
        pass
        
    def saveHandler(self, human, file):
        pass

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

    def onMouseEntered(self, event):
        pass

    def onMouseExited(self, event):
        pass


def setColorForFaceGroup(mesh, fgName, color):
    color = np.asarray(color, dtype=np.uint8)
    mesh.color[mesh.getVerticesForGroups([fgName])] = color[None,:]
    mesh.markCoords(colr=True)
    mesh.sync_color()


def load(app):
    category = app.getCategory('Library')
    taskview = category.addTask(AnimationLibrary(category))

    app.addLoadHandler('animations', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    pass
