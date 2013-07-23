#!/usr/bin/python
# -*- coding: utf-8 -*-

import gui3d, gui
import module3d
import log
import mh
import bvh
import skeleton
import skeleton_drawing
import animation
import sys, os

import numpy as np
import numpy.linalg as la
import transformations as tm


# Retarget method
# 1  old approach (manually defined rotation offsets) 
# 2  new auto mapping (only compensate for legs)
# 3  new auto mapping (compensate for all bones except spine bones)
METHOD = 2

# Set to true to let target skeleton shine through human
SKELETON_SHOWTHROUGH = True

# Set to true to draw BVH rig in its rest pose
DRAW_BVH_SOURCE = False

class AnimTestView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Retarget Test')

        self.human = gui3d.app.selectedHuman
        self.firstTime = True

        self.skelObj = None
        self.bvhObj = None
        
    def doFirstTime(self):
        # Load BVH source rig and animation
        bvhRig = bvh.load(mh.getSysDataPath('bvhs/cmu/12_03.bvh'))
        bvhSkel = bvhRig.createSkeleton()   # TODO debug and find out why it creates some zero-length bones (such as hand)

        # Draw static BVH mesh in rest pose
        if DRAW_BVH_SOURCE:
            bvhMesh = skeleton_drawing.meshFromSkeleton(bvhSkel, "Prism")

            bvhObj = gui3d.app.addObject(gui3d.Object(self.human.getPosition(), bvhMesh) )
            bvhObj.setRotation(self.human.getRotation())
            self.bvhObj = bvhObj

            bvhMesh.priority = 100
            bvhMesh.setPickable(True)
            mh.updatePickingBuffer()
            bvhMesh.setColor([0, 255, 0, 255])

            @self.bvhObj.mhEvent
            def onMouseEntered(event):
                """
                Event fired when mouse hovers over a skeleton mesh facegroup
                """
                gui3d.app.statusPersist(event.group.name)


        # Load target rig
        skel,weights = skeleton.loadRig(mh.getSysDataPath('rigs/soft1.rig'), self.human.meshData)
        skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")

        # Draw target rig
        skelObj = gui3d.app.addObject(gui3d.Object(self.human.getPosition(), skelMesh) )
        skelObj.setRotation(self.human.getRotation())
        self.skelObj = skelObj
        skelMesh.priority = 100
        skelMesh.setPickable(True)
        mh.updatePickingBuffer()

        @self.skelObj.mhEvent
        def onMouseEntered(event):
            """
            Event fired when mouse hovers over a skeleton mesh facegroup
            """
            gui3d.app.statusPersist(event.group.name)

        # Animate target skeleton together with human
        skelWeights = skeleton_drawing.getVertBoneMapping(skel, skelMesh)
        skelAMesh = animation.AnimatedMesh(skel, skelMesh, skelWeights)
        skelAMesh.addMesh(self.human.meshData, weights)


        ### Interesting part starts here #######################################

        # Determine pose to place target rig in the same rest pose as src bvh rig
        pose = animation.emptyPose(skel.getBoneCount())
        # Load a joint mapping from mb.src to soft1 rig (no .tgt needed as it has the MHX bones)
        jointToBoneMap = skeleton.getRetargetMapping('mb', 'soft1', skel)
        bvhSkel.canonalizeBoneNames()
        if METHOD > 1:
            for bIdx, tgtBone in enumerate(skel.getBones()):
                srcName, _ = jointToBoneMap[bIdx]
                if not srcName:
                    continue
                srcBone = bvhSkel.getBone(srcName)
                srcGlobalOrient = srcBone.matRestGlobal.copy()
                srcGlobalOrient[:3,3] = 0.0  # No translation, only rotation
                tgtGlobalOrient = np.mat(tgtBone.matPoseGlobal.copy()) # Depends on pose compensation of parent bones
                tgtGlobalOrient[:3,3] = 0.0


                if METHOD == 2:
                    if not tgtBone.name in ["UpLeg_L", "UpLeg_R", "LoLeg_L", "LoLeg_R", "Foot_L", "Foot_R"]:
                        log.message("Do not compensate %s", tgtBone.name)
                        continue

                if srcBone.length == 0:
                    # Safeguard because this always leads to wrong pointing target bones
                    # I have no idea why, but for some reason the skeleton created from the BVH 
                    # has some zero-sized bones (this is probably a bug)
                    log.message("skipping zero-length (source) bone %s", srcBone.name)
                    continue

                if tgtBone.length == 0:
                    log.message("skipping zero-length (target) bone %s", tgtBone.name)
                    continue

                # Never compensate for spine bones, as this ususally deforms the mesh heavily
                if tgtBone.name in ["Root", "Hips", "Spine1", "Spine2", "Spine3"]:
                    log.message("Skipping non-compensated bone %s", tgtBone.name)
                    continue

                log.message("compensating %s", tgtBone.name)
                log.debug(str(srcGlobalOrient))
                log.debug(str(tgtGlobalOrient))

                diff = np.mat(la.inv(tgtGlobalOrient)) * srcGlobalOrient
                # Rotation only
                diff[:3,3] = 0.0
                diffPose = tgtGlobalOrient * diff * np.mat(la.inv(tgtGlobalOrient))
                pose[bIdx] = diffPose
                log.debug(str(diffPose))

                # Set pose that orients target bone in the same orientation as the source bone in rest
                tgtBone.matPose = np.mat(la.inv(tgtBone.matRestGlobal)) * diffPose * np.mat(tgtBone.matRestGlobal)

                skel.update()   # Update skeleton after each modification of a bone

        # Add pose (animation with 1 frame) to target skeleton for visualizing
        poseAnimTrack = animation.AnimationTrack("SrcRestPose", pose, 1, 1)
        skelAMesh.addAnimation(poseAnimTrack)
        skelAMesh.setActiveAnimation(poseAnimTrack.name)
        skelAMesh.setAnimateInPlace(True)
        skelAMesh.setToFrame(0)
        self.aMesh = skelAMesh

        # Load animation with compensation
        if METHOD > 1:
            jointToBoneMap = [ boneName for boneName, _ in jointToBoneMap ] # Remove other compensation
        anim = bvhRig.createAnimationTrack(jointToBoneMap)
        anim.sparsify(30)
        if METHOD > 1:
            nBones = skel.getBoneCount()
            # Compensate animation frames
            for frameIdx in xrange(anim.nFrames):
                for bIdx in xrange(nBones):
                    i = (frameIdx*nBones)+ bIdx
                    anim.data[i] = np.mat(anim.data[i]) * np.mat(pose[bIdx])

        # Set retargeted animation to target skeleton
        skelAMesh.addAnimation(anim)
        skelAMesh.setActiveAnimation(anim.name)
        skelAMesh.setAnimateInPlace(True)
        skelAMesh.setToFrame(1)
        self.animTrack = anim


    ### Interesting part stops here ############################################


    def onShow(self, event):
        if SKELETON_SHOWTHROUGH:
            self.human.meshData.setTransparentPrimitives(len(self.human.meshData.fvert))
        if self.firstTime:
            self.doFirstTime()
            self.firstTime = False

        #self.aMesh.setToFrame(0)
        self.aMesh.setToFrame(1)
        self.frameIdx = 1
        self.timer = mh.addTimer(max(30, int(1.0/self.animTrack.frameRate * 1000)), self.onFrameChanged)

    def onHide(self, event):
        mh.removeTimer(self.timer)

    def onFrameChanged(self):
        self.frameIdx = self.frameIdx + 1
        if self.frameIdx > self.animTrack.nFrames:
            self.frameIdx = 0
        self.aMesh.setToFrame(self.frameIdx)
        gui3d.app.redraw()

    def onHumanRotated(self, event):
        if self.skelObj:
            self.skelObj.setRotation(self.human.getRotation())
        if DRAW_BVH_SOURCE:
            if self.bvhObj:
                self.bvhObj.setRotation(self.human.getRotation())

    def onHumanTranslated(self, event):
        if self.skelObj:
            self.skelObj.setPosition(self.human.getPosition())
        if DRAW_BVH_SOURCE:
            if self.bvhObj:
                self.bvhObj.setPosition(self.human.getPosition())



category = None
taskview = None

def load(app):
    category = app.getCategory('Pose/Animate')
    taskview = category.addTask(AnimTestView(category))

    log.message('Anim test loaded')


def unload(app):
    pass

