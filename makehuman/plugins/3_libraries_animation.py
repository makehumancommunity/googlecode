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


class AnimationCollection(object):
    def __init__(self, path):
        self.path = path
        self.uuid = None
        self.rig = None
        self.tags = set()
        self.animations = []
        self.scale = 1.0

    def getAnimation(self, name):
        for anim in self.animations:
            if anim.name == name:
                return anim

class Animation(object):
    def __init__(self, name):
        self.name = name
        self.bvh = None
        self.options = []
        self.collection = None

    def getPath(self):
        folder = os.path.dirname(self.collection.path)
        return os.path.join(folder, self.bvh)

class AnimationLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Animations')

        self.systemAnims = os.path.join('data', 'animations')
        self.userAnims = os.path.join(mh.getPath(''), 'data', 'animations')
        self.animPaths = [self.userAnims, self.systemAnims]
        self.extension = "mhanim"

        # Test config param
        self.perFramePlayback = False   # Set to false to use time for playback

        self.interpolate = True     # Only useful when using time for playback

        self.skelMesh = None
        self.skelObj = None

        self.bvhRig = None
        self.animations = []
        self.anim = None
        self.collections = {}

        self.tags = set()

        self.lastSkeleton = None
        self.human = gui3d.app.selectedHuman
        self.oldHumanTransp = self.human.meshData.transparentPrimitives

        # Stores all selected animations and makes them available globally
        self.human.animations = []

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
                self.setHumanTransparency(True)
            else:
                self.skelObj.hide()
                self.setHumanTransparency(False)
        self.showSkeletonTggl.setSelected(True)

        self.createPlaybackControl()

        self.animationSelector = []
        self.animationsBox = self.addRightWidget(gui.GroupBox('Animations'))

        self.tagsBox = self.addLeftWidget(gui.GroupBox('Tags'))
        self.tagSelector = []

    def reloadAnimations(self):
        # Clear up old animations cache
        self.animations = []
        self.anim = None
        for radioBtn in self.animationSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.animationSelector = []
        if self.human.animated:
            self.human.animated.removeAnimations()

        for tgglBtn in self.tagSelector:
            tgglBtn.hide()
            tgglBtn.destroy()
        self.tagSelector = []

        # Reload animations list
        self.animations = self.getAnimations()

        for anim in self.animations:
            if anim.collection.uuid not in self.collections.keys():
                self.collections[anim.collection.uuid] = anim.collection

        # Create a list of all animations in the GUI
        self.tags = set()
        for anim in self.animations:
            radioBtn = self.animationsBox.addWidget(gui.RadioButton(self.animationSelector, anim.name, selected=len(self.animationSelector) == 0))
            radioBtn.anim = anim

            @radioBtn.mhEvent
            def onClicked(event):
                for rdio in self.animationSelector:
                    if rdio.selected:
                        self.highlightAnimation(rdio.anim)

        for collection in self.collections.values():
            self.tags = self.tags.union(collection.tags)

        # Create tag list in GUI
        for tag in self.tags:
            btn = self.tagsBox.addWidget(gui.ToggleButton(tag))
            btn.tag = tag
            self.tagSelector.append(btn)
            btn.setSelected(True)

            @btn.mhEvent
            def onClicked(event):
                self.filterBySelectedTags()

        self.highlightAnimation(self.animationSelector[0].anim)

    def filterBySelectedTags(self):
        tags = self.getSelectedTags()
        for radioBtn in self.animationSelector:
            if tags.intersection(radioBtn.anim.collection.tags):
                radioBtn.show()
            else:
                radioBtn.hide()

    def getSelectedTags(self):
        tags = set()
        for tgglBtn in self.tagSelector:
            if tgglBtn.selected:
                tags.add(tgglBtn.tag)
        return tags

    def loadAnimation(self, uuid, animName):
        if not human.skeleton:
            log.error("Cannot load animations when no skeleton is selected.")
            gui3d.app.statusPersist("Error: cannot load animations when no skeleton is selected.")
            return

        # Cache all animation collection files
        if len(self.animations) == 0:
            self.reloadAnimations()

        if not uuid in self.collections.keys():
            return

        collection = self.collections[uuid]
        anim = collection.getAnimation(animName)

        self.chooseAnimation(anim)

    def getAnimations(self):
        """
        Find and parse all animation collection files.
        """
        animations = []

        mhAnimFiles = searchFiles(self.animPaths, [self.extension])
        for filename in mhAnimFiles:
            mhAnim = readAnimCollectionFile(filename)
            if mhAnim:
                animations.extend( mhAnim.animations )
            else:
                log.debug("Failed to parse mhanim file %s", filename)
        return animations

    def loadBVH(self, anim):
        """
        Load animation from a BVH file.
        """
        if "z_is_up" in anim.options:
            swapYZ = True
        else:
            swapYZ = False

        log.debug("Loading BVH %s", anim.getPath())

        # Load BVH data
        bvhRig = bvh.load(anim.getPath(), swapYZ)
        if anim.collection.scale != 1.0:
            # Scale rig
            bvhRig.scale(scale)
            # Scale is only useful when using the joint locations of the BVH rig
            # or when drawing the BVH rig.

        if self.human.skeleton.name == anim.collection.rig:
            # Skeleton and joint rig in BVH match, do a straight mapping of the
            # motion:

            # Load animation data from BVH file and add it to AnimatedMesh
            # This is a list that references a joint name in the BVH for each 
            # bone in the skeleton (breadth-first order):
            jointToBoneMap = [bone.name for bone in self.human.skeleton.getBones()]
            animTrack = bvhRig.createAnimationTrack(jointToBoneMap, getAnimationTrackName(anim.collection.uuid, anim.name))
            gui3d.app.statusPersist("")
        else:
            # Skeleton and joint rig in BVH are not the same, retarget/remap
            # the motion data:

            # TODO implement retarget/remap
            gui3d.app.statusPersist("Animation loading is currently only implemented for the same rig as in BVH. Try selecting the %s skeleton from the skeleton library.", anim.collection.rig)
            return None

        log.debug("Created animation track for %s rig.", self.human.skeleton.name)

        # Sparsify data to test out interpolation
        log.debug("sparsifying anim with framerate %s to %s", animTrack.frameRate, 10)
        animTrack.sparsify(10)
        animTrack.interpolationType = 1 if self.interpolate else 0

        log.debug("Frames: %s", animTrack.nFrames)
        log.debug("Playtime: %s", animTrack.getPlaytime())

        return animTrack

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        if not self.human.skeleton:
            gui3d.app.statusPersist("No skeleton selected. Please select a skeleton rig from the Skeleton library first.")
            return

        # Detect when skeleton has changed
        if self.human.skeleton and self.lastSkeleton and \
           self.lastSkeleton != self.human.skeleton.name:
            # Removed cached animation tracks (as they are mapped to a specific skeleton)
            self.human.animated.removeAnimations()
            self.anim = None

        if self.human.skeleton:
            self.lastSkeleton = self.human.skeleton.name
        else:
            self.lastSkeleton = None

        self.skelObj = self.human.skeletonObject
        self.skelMesh = self.skelObj.mesh

        if self.skelObj:
            self.skelObj.show()
            # Show skeleton through human 
            self.oldHumanTransp = self.human.meshData.transparentPrimitives
            self.setHumanTransparency(True)
            self.human.meshData.setPickable(False)

        self.frameSlider.setValue(0)

        # Only load mhanim files at first time or when "Reload" button is pressed
        if len(self.animations) == 0:
            self.reloadAnimations()
        elif self.anim:
            self.startPlayback()
        else:
            self.highlightAnimation(self.animations[0])

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        self.setToRestPose()
        self.setHumanTransparency(False)
        self.human.meshData.setPickable(True)

        if self.skelObj:
            self.skelObj.hide()

        self.skelObj = None 
        self.skelMesh = None

    def createPlaybackControl(self):
        self.playbackBox = self.addRightWidget(gui.GroupBox('Playback'))
        self.frameSlider = self.playbackBox.addWidget(gui.Slider(value = 0, min = 0, max = 1, label = 'Frame: %d'))
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
            self.human.animated.setAnimateInPlace(self.animateInPlaceTggl.selected)
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
        if self.timer:
            mh.removeTimer(self.timer)
            self.timer = None
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
        if not self.human.animated:
            return
        self.stopPlayback()
        self.human.animated.setToRestPose()

    def chooseAnimation(self, anim):
        if not anim in self.human.animations:
            self.animations.append(anim)

    def highlightAnimation(self, anim):
        self.stopPlayback()
        if not self.human.skeleton:
            return

        if not self.human.animated.hasAnimation(getAnimationTrackName(anim.collection.uuid, anim.name)):
            # Load animation track (containing the actual animation data)
            # Actually loading the BVH is only necessary when previewing the
            # animation or exporting when the human is exported
            animationTrack = self.loadBVH(anim)
            if not animationTrack:
                return
            self.human.animated.addAnimation(animationTrack)

        self.human.animated.setActiveAnimation(getAnimationTrackName(anim.collection.uuid, anim.name))
        self.anim = self.human.animated.getAnimation(getAnimationTrackName(anim.collection.uuid, anim.name))
        log.debug("Setting animation to %s", anim.name)

        self.human.animated.setAnimateInPlace(self.animateInPlaceTggl.selected)

        if self.frameSlider:
            self.frameSlider.setMin(0)
            maxFrame = self.anim.nFrames-1
            if maxFrame < 1:
                maxFrame = 1
            self.frameSlider.setMax(maxFrame)
            self.currFrame = 0
            self.frameSlider.setValue(0)
        self.updateAnimation(0)
        gui3d.app.redraw()

        self.startPlayback()

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
            self.human.animated.setActiveAnimation(self.anim.name)
            self.anim.interpolationType = 1 if self.interpolate else 0
            self.human.animated.update(1.0/30.0)
            frame = self.anim.getFrameIndexAtTime(self.human.animated.getTime())[0]
            self.frameSlider.setValue(frame)
        gui3d.app.redraw()

    def updateAnimation(self, frame):
        if not self.anim or not self.human.skeleton:
            return
        self.currFrame = frame
        self.human.animated.setActiveAnimation(self.anim.name)
        self.anim.interpolationType = 1 if self.interpolate else 0
        self.human.animated.setToFrame(frame)

    def setHumanTransparency(self, enabled):
        if enabled:
            self.human.meshData.setTransparentPrimitives(len(self.human.meshData.fvert))
        else:
            self.human.meshData.setTransparentPrimitives(self.oldHumanTransp)

    def loadHandler(self, human, values):
        if values[0] == "animations" and len(values) >= 3:
            uuid = values[1]
            animName = values[2]

            '''
            mhanim = exportutils.config.getExistingProxyFile(None, uuid, "animations")
            if not mhanim:
                log.notice("Animation %s (%s) does not exist. Skipping.", animName, uuid)
                return
            self.loadAnimation(human, mhanim, animName)
            '''

            self.loadAnimation(uuid, animName)        

    def saveHandler(self, human, file):
        if self.human.animated and self.human.skeleton:
            for anim in self.human.animations:
                file.write('animations %s %s\n' % (anim.collection.uuid, anim.name))

    def onHumanRotated(self, event):
        if self.skelObj:
            self.skelObj.setRotation(gui3d.app.selectedHuman.getRotation())

    def onHumanTranslated(self, event):
        if self.skelObj:
            self.skelObj.setPosition(gui3d.app.selectedHuman.getPosition())

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


def readAnimCollectionFile(filename):
    """
    Parse a .mhanim file.
    """
    try:
        fh = open(filename, "rU")
    except:
        return None

    anims = AnimationCollection(filename)

    for line in fh:
        words = line.split()
        if len(words) == 0:
            pass

        elif words[0] == '#':
            if len(words) == 1:
                continue

            key = words[1]

            if key == 'uuid':
                anims.uuid = " ".join(words[2:])
            elif key == 'tag':
                anims.tags.add( " ".join(words[2:]) )
            elif key == 'rig':
                anims.rig = ( " ".join(words[2:]) )
            elif key == 'scale':
                anims.scale = float(words[2])
            elif key == 'anim':
                anim = Animation(name = words[2])
                anim.options = words[4:]
                anim.bvh = words[3]
                anim.collection = anims

                anims.animations.append(anim)
            else:
                # Unknown keyword
                pass
    return anims

def getAnimationTrackName(collectionUuid, animationName):
    return "%s_%s" % (collectionUuid, animationName)

def searchFiles(paths, extensions):
    # TODO move this method somewhere to a shared module?
    for path in paths:
        for root, dirs, files in os.walk(path):
            for f in files:
                ext = os.path.splitext(f)[1][1:].lower()
                if ext in extensions:
                    if f.lower().endswith('.' + ext):
                        yield os.path.join(root, f)

