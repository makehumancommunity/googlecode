# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

#
#   M_b = global bone matrix, relative world (PoseBone.matrix)
#   L_b = local bone matrix, relative parent and rest (PoseBone.matrix_local)
#   R_b = bone rest matrix, relative armature (Bone.matrix_local)
#   T_b = global T-pose marix, relative world
#
#   M_b = M_p R_p^-1 R_b L_b
#   M_b = A_b M'_b
#   T_b = A_b T'_b
#   A_b = T_b T'^-1_b
#   B_b = R^-1_b R_p
#
#   L_b = R^-1_b R_p M^-1_p A_b M'_b
#   L_b = B_b M^-1_p A_b M'_b
#


import bpy
import mathutils
import time
from collections import OrderedDict
from mathutils import *
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

from . import props, source, target, load, simplify, t_pose
from . import mcp
from .utils import *


class CAnimation:

    def __init__(self, srcRig, trgRig, boneAssoc):
        self.srcRig = srcRig
        self.trgRig = trgRig
        self.boneAnims = OrderedDict()

        for (trgName, srcName) in boneAssoc:
            try:
                trgBone = trgRig.pose.bones[trgName]
                srcBone = srcRig.pose.bones[srcName]
            except KeyError:
                print("  -", trgName, srcName)
                continue
            banim = self.boneAnims[trgName] = CBoneAnim(srcBone, trgBone, self)


    def printResult(self, scn, frame):
        scn.frame_set(frame)
        for name in ["LeftHip"]:
            banim = self.boneAnims[name]
            banim.printResult(frame)


    def setTPose(self, scn):
        selectAndSetRestPose(self.srcRig, scn)
        t_pose.setTPose(self.srcRig, scn)
        selectAndSetRestPose(self.trgRig, scn)
        if isMakeHumanRig(self.trgRig) and scn.McpMakeHumanTPose:
            tpose = "target_rigs/makehuman_tpose.json"
        else:
            tpose = None
        t_pose.setTPose(self.trgRig, scn, filename=tpose)
        for banim in self.boneAnims.values():
            banim.insertTPoseFrame()
        scn.frame_set(0)
        for banim in self.boneAnims.values():
            banim.getTPoseMatrix()


    def retarget(self, frames, scn):
        objects = hideObjects(scn, self.srcRig)
        try:
            for frame in frames:
                scn.frame_set(frame)
                for banim in self.boneAnims.values():
                    banim.retarget(frame)
        finally:
            unhideObjects(objects)


class CBoneAnim:

    def __init__(self, srcBone, trgBone, anim):
        self.name = srcBone.name
        self.srcMatrices = {}
        self.trgMatrices = {}
        self.srcMatrix = None
        self.trgMatrix = None
        self.srcBone = srcBone
        self.trgBone = trgBone
        self.aMatrix = None
        self.parent = self.getParent(trgBone, anim)
        if self.parent:
            self.trgBone.McpParent = self.parent.trgBone.name
            trgParent = self.parent.trgBone
            self.bMatrix = trgBone.bone.matrix_local.inverted() * trgParent.bone.matrix_local
        else:
            self.bMatrix = trgBone.bone.matrix_local.inverted()


    def __repr__(self):
        if self.parent:
            parname = self.parent.name
        else:
            parname = None
        return (
            "<CBoneAnim %s\n" % self.name +
            "  src %s\n" % self.srcBone.name +
            "  trg %s\n" % self.trgBone.name +
            "  par %s\n" % parname +
            "  A %s\n" % self.aMatrix +
            "  B %s\n" % self.bMatrix)


    def printResult(self, frame):
        print(
            "Retarget %s => %s\n" % (self.srcBone.name, self.trgBone.name) +
            "S %s\n" % self.srcBone.matrix +
            "T %s\n" % self.trgBone.matrix +
            "R %s\n" % (self.trgBone.matrix * self.srcBone.matrix.inverted())
            )


    def getParent(self, pb, anim):
        pb = pb.parent
        while pb:
            if pb.McpBone:
                try:
                    return anim.boneAnims[pb.name]
                except KeyError:
                    pass

            subtar = None
            for cns in pb.constraints:
                if (cns.type[0:4] == "COPY" and
                    cns.influence > 0.8):
                    subtar = cns.subtarget

            if subtar:
                pb = anim.trgRig.pose.bones[subtar]
            else:
                pb = pb.parent
        return None


    def insertKeyFrame(self, mat, frame):
        pb = self.trgBone
        setRotation(pb, mat, frame, pb.name)
        if not self.parent:
            pb.location = mat.to_translation()
            pb.keyframe_insert("location", frame=frame, group=pb.name)


    def insertTPoseFrame(self):
        mat = t_pose.getStoredBonePose(self.trgBone)
        self.insertKeyFrame(mat, 0)


    def getTPoseMatrix(self):
        self.aMatrix =  self.srcBone.matrix.inverted() * self.trgBone.matrix
        if not isRotationMatrix(self.trgBone.matrix):
            halt
        if not isRotationMatrix(self.srcBone.matrix):
            halt
        if not isRotationMatrix(self.aMatrix):
            halt


    def retarget(self, frame):
        self.srcMatrix = self.srcBone.matrix.copy()
        self.trgMatrix = self.srcMatrix * self.aMatrix
        self.trgMatrix.col[3] = self.srcMatrix.col[3]
        self.srcMatrices[frame] = self.srcMatrix
        self.trgMatrices[frame] = self.trgMatrix
        if self.parent:
            mat1 = self.parent.trgMatrix.inverted() * self.trgMatrix
        else:
            mat1 = self.trgMatrix
        mat2 = self.bMatrix * mat1
        self.insertKeyFrame(mat2, frame)
        return

        if self.name == "upper_arm.L":
            print()
            print(self)
            print("S ", self.srcMatrix)
            print("T ", self.trgMatrix)
            print(self.parent.name)
            print("TP", self.parent.trgMatrix)
            print("M1", mat1)
            print("M2", mat2)
            print("MB2", self.trgBone.matrix)


def hideObjects(scn, rig):
    objects = []
    for ob in scn.objects:
        if ob != rig:
            objects.append((ob, list(ob.layers)))
            ob.layers = 20*[False]
    return objects


def unhideObjects(objects):
    for (ob,layers) in objects:
        ob.layers = layers
    return


def clearMcpProps(rig):
    keys = list(rig.keys())
    for key in keys:
        if key[0:3] == "Mcp":
            del rig[key]

    for pb in rig.pose.bones:
        keys = list(pb.keys())
        for key in keys:
            if key[0:3] == "Mcp":
                del pb[key]


def retargetAnimation(context, srcRig, trgRig):
    scn = context.scene
    setMhxIk(trgRig, True, True, False)
    frames = getActiveFrames(srcRig)
    scn.objects.active = trgRig
    if trgRig.animation_data:
        trgRig.animation_data.action = None
    scn.update()

    if isRigify(trgRig):
        setRigifyFKIK(trgRig, 0)

    try:
        scn.frame_current = frames[0]
    except:
        raise MocapError("No frames found.")
    oldData = changeTargetData(trgRig)

    source.ensureSourceInited(scn)
    source.setArmature(srcRig, scn)
    print("Retarget %s --> %s" % (srcRig.name, trgRig.name))

    target.ensureTargetInited(scn)
    boneAssoc = target.getTargetArmature(trgRig, scn)
    anim = CAnimation(srcRig, trgRig, boneAssoc)
    anim.setTPose(scn)

    frameBlock = frames[0:100]
    index = 0
    try:
        while frameBlock:
            print(frames[index])
            anim.retarget(frameBlock, scn)
            index += 100
            frameBlock = frames[index:index+100]

        scn.frame_current = frames[0]
    finally:
        restoreTargetData(trgRig, oldData)

    #anim.printResult(scn, 1)

    setInterpolation(trgRig)
    act = trgRig.animation_data.action
    act.name = trgRig.name[:4] + srcRig.name[2:]
    act.use_fake_user = True
    print("Retargeted %s --> %s" % (srcRig.name, trgRig.name))


#
#   changeTargetData(rig):
#   restoreTargetData(rig, data):
#

def changeTargetData(rig):
    tempProps = [
        ("MhaRotationLimits", 0.0),
        ("MhaArmIk_L", 0.0),
        ("MhaArmIk_R", 0.0),
        ("MhaLegIk_L", 0.0),
        ("MhaLegIk_R", 0.0),
        ("MhaSpineIk", 0),
        ("MhaSpineInvert", 0),
        ("MhaElbowPlant_L", 0),
        ("MhaElbowPlant_R", 0),
        ]

    props = []
    for (key, value) in tempProps:
        try:
            props.append((key, rig[key]))
            rig[key] = value
        except KeyError:
            pass

    permProps = [
        ("MhaElbowFollowsShoulder", 0),
        ("MhaElbowFollowsWrist", 0),
        ("MhaKneeFollowsHip", 0),
        ("MhaKneeFollowsFoot", 0),
        ("MhaArmHinge", 0),
        ]

    for (key, value) in permProps:
        try:
            rig[key+"_L"]
            rig[key+"_L"] = value
            rig[key+"_R"] = value
        except KeyError:
            pass

    layers = list(rig.data.layers)
    rig.data.layers = 32*[True]
    locks = []
    for pb in rig.pose.bones:
        constraints = []
        for cns in pb.constraints:
            if cns.type == 'LIMIT_DISTANCE':
                cns.mute = True
            elif cns.type[0:6] == 'LIMIT':
                constraints.append( (cns, cns.mute) )
                cns.mute = True
        locks.append( (pb, list(pb.lock_location), list(pb.lock_rotation), list(pb.lock_scale), constraints) )
        pb.lock_location = [False, False, False]
        pb.lock_rotation = [False, False, False]
        pb.lock_scale = [False, False, False]

    norotBones = []
    return (props, layers, locks, norotBones)


def restoreTargetData(rig, data):
    (props, rig.data.layers, locks, norotBones) = data

    for (key,value) in props:
        rig[key] = value

    for b in norotBones:
        b.use_inherit_rotation = True

    for lock in locks:
        (pb, lockLoc, lockRot, lockScale, constraints) = lock
        pb.lock_location = lockLoc
        pb.lock_rotation = lockRot
        pb.lock_scale = lockScale
        for (cns, mute) in constraints:
            cns.mute = mute


#
#    loadRetargetSimplify(context, filepath):
#

def loadRetargetSimplify(context, filepath):
    print("\nLoad and retarget %s" % filepath)
    time1 = time.clock()
    scn = context.scene
    trgRig = context.object
    clearMcpProps(trgRig)
    srcRig = load.readBvhFile(context, filepath, scn, False)
    layers = list(trgRig.data.layers)
    load.renameAndRescaleBvh(context, srcRig, trgRig)
    retargetAnimation(context, srcRig, trgRig)
    scn = context.scene
    if scn.McpDoSimplify:
        simplify.simplifyFCurves(context, trgRig, False, False)
    if scn.McpRescale:
        simplify.rescaleFCurves(context, trgRig, scn.McpRescaleFactor)
    load.deleteSourceRig(context, srcRig, 'Y_')
    trgRig.data.layers = layers
    time2 = time.clock()
    print("%s finished in %.3f s" % (filepath, time2-time1))
    return


########################################################################
#
#   Buttons
#

class VIEW3D_OT_NewRetargetMhxButton(bpy.types.Operator):
    bl_idname = "mcp.retarget_mhx"
    bl_label = "Retarget Selected To Active"
    bl_options = {'UNDO'}

    def execute(self, context):
        print()
        print()
        try:
            trgRig = context.object
            rigList = list(context.selected_objects)
            scn = context.scene
            target.getTargetArmature(trgRig, scn)
            for srcRig in rigList:
                if srcRig != trgRig:
                    retargetAnimation(context, srcRig, trgRig)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_LoadAndRetargetButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_and_retarget"
    bl_label = "Load And Retarget"
    bl_options = {'UNDO'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        try:
            loadRetargetSimplify(context, self.properties.filepath)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_ClearTempPropsButton(bpy.types.Operator):
    bl_idname = "mcp.clear_temp_props"
    bl_label = "Clear Temporary Properties"
    bl_description = "Clear properaties used by MakeWalk. Animation editing may fail after this."
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            clearMcpProps(context.object)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}
