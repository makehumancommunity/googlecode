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



import bpy, os, mathutils, math, time
from math import sin, cos
from mathutils import *
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

from . import utils, props, source, target, load, simplify
#from .target_rigs import rig_mhx
from . import mcp
from .utils import *

#
#   class CBoneData:
#

class CBoneData:
    def __init__(self, srcBone, trgBone):
        self.name = srcBone.name
        self.parent = None
        self.srcMatrices = {}
        self.srcPoseBone = srcBone
        self.trgPoseBone = trgBone
        self.trgRestMat = None
        self.trgRestInv = None
        self.trgBakeMat = None
        self.trgBakeInv = None
        self.trgOffset = None
        self.rotOffset = None
        self.rotOffsInv = None
        self.rollMat = None
        self.rollInv = None
        return

#class CMatrixGroup:
#    def __init__(self, srcMat, frame):
#        self.frame = frame
#        self.srcMatrix = srcMat.copy()
#        return
#
#    def __repr__(self):
#        return "<CMat %d %s>" % (self.frame, self.srcMatrix)


class CAnimation:
    def __init__(self, srcRig, trgRig):
        self.srcRig = srcRig
        self.trgRig = trgRig
        self.boneDatas = {}
        self.boneDataList = []
        return

#
#
#

KeepRotationOffset = ["hips", "pelvis", "hips", "hip.L", "hip.R"]
ClavBones = ["shoulder.L", "shoulder.R"]
SpineBones = ["spine", "spine-1", "chest", "chest-1", "neck", "head"]
#FootBones = []
#IgnoreBones = []
FootBones = ["foot.L", "foot.R", "toe.L", "toe.R"]
IgnoreBones = ["toe.L", "toe.R"]

#
#
#


def setTranslation(mat, loc):
    for m in range(3):
        mat[m][3] = loc[m][3]


def setTranslationVec(mat, loc):
    for m in range(3):
        mat[m][3] = loc[m]


def setRotation(mat, rot):
    for m in range(3):
        for n in range(3):
            mat[m][n] = rot[m][n]


def keepRollOnly(mat):
    for n in range(4):
        mat[1][n] = 0
        mat[n][1] = 0
        mat[3][n] = 0
        mat[n][3] = 0
    mat[1][1] = 1

#
#   retargetFkBone(boneData, frame):
#

def retargetFkBone(boneData, frame):
    srcBone = boneData.srcPoseBone
    trgBone = boneData.trgPoseBone
    name = srcBone.name
    srcMatrix = boneData.srcMatrices[frame]
    srcRot = srcMatrix  #* srcData.rig.matrix_world
    bakeMat = srcMatrix

    # Set translation offset
    parent = boneData.parent
    if parent:
        parMat = parent.srcMatrices[frame]
        parInv = parMat.inverted()
        loc = parMat * boneData.trgOffset
        setTranslation(bakeMat, loc)
        bakeMat = parInv * bakeMat

        if parent.rollMat:
            #roll = utils.getRollMat(parent.rollMat)
            #print("ParRoll", name, parent.name, roll*Rad2Deg)
            bakeRot = parent.rollInv * bakeMat
            setRotation(bakeMat, bakeRot)
        elif parent.rotOffsInv:
            bakeRot = parent.rotOffsInv * bakeMat
            setRotation(bakeMat, bakeRot)

        parRest = parent.trgRestMat
        bakeMat = parRest * bakeMat
    else:
        parMat = None
        parRotInv = None

    # Set rotation offset
    if boneData.rotOffset:
        rot = boneData.rotOffset
        if parent and parent.rotOffsInv:
            rot = rot * parent.rotOffsInv
        bakeRot = bakeMat * rot
        setRotation(bakeMat, bakeRot)
    else:
        rot = None

    trgMat = boneData.trgRestInv * bakeMat

    if boneData.rollMat:
        #roll = utils.getRollMat(boneData.rollMat)
        #print("SelfRoll", name, roll*Rad2Deg)
        trgRot = trgMat * boneData.rollMat
        setRotation(trgMat, trgRot)
        #utils.printMat4(" Trg2", trgMat, "  ")
        #halt

    trgBone.matrix_basis = trgMat
    if 0 and trgBone.name == "Hip_L":
        print(name)
        utils.printMat4(" PM", parMat, "  ")
        utils.printMat4(" PR", parent.rotOffsInv, "  ")
        utils.printMat4(" RO", boneData.rotOffset, "  ")
        utils.printMat4(" BR", bakeRot, "  ")
        utils.printMat4(" BM", bakeMat, "  ")
        utils.printMat4(" Trg", trgMat, "  ")
        #halt

    if trgBone.name in IgnoreBones:
        trgBone.rotation_quaternion = (1,0,0,0)

    utils.insertRotationKeyFrame(trgBone, frame)
    if not boneData.parent:
        trgBone.keyframe_insert("location", frame=frame, group=trgBone.name)
    return

#
#   collectSrcMats(anim, frames, scn):
#

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


def collectSrcMats(anim, frames, scn):
    objects = hideObjects(scn, anim.srcRig)
    try:
        for frame in frames:
            scn.frame_set(frame)
            if frame % 100 == 0:
                print("Collect", int(frame))
            for boneData in anim.boneDataList:
                boneData.srcMatrices[frame] = boneData.srcPoseBone.matrix.copy()
    finally:
        unhideObjects(objects)
    return

#
#   retargetMatrices(anim, frames, first, doFK, doIK, scn):
#

def retargetMatrices(anim, frames, first, doFK, doIK, scn):
    for frame in frames:
        if frame % 100 == 0:
            print("Retarget", int(frame))
        if doFK:
            for boneData in anim.boneDataList:
                retargetFkBone(boneData, frame)
        else:
            scn.frame_set(frame)
        if doIK:
            retargetIkBones(anim.trgRig, frame, first)
            first = False
    return

#
#   setupFkBones(srcRig, trgRig, boneAssoc, parAssoc, anim, scn):
#

def getParent(parName, parAssoc, trgRig, anim):
    if not parName:
        return None
    try:
        trgParent = trgRig.pose.bones[parName]
    except KeyError:
        return None
    try:
        anim.boneDatas[trgParent.name]
        return trgParent
    except        :
        pass
    return getParent(parAssoc[trgParent.name], parAssoc, trgRig, anim)


def setupFkBones(srcRig, trgRig, boneAssoc, parAssoc, anim, scn):
    keepOffsets = KeepRotationOffset + FootBones
    keepOffsInverts = []
    if scn.McpUseSpineOffset:
        keepOffsets += SpineBones
        keepOffsInverts += SpineBones
    if scn.McpUseClavOffset:
        keepOffsets += ClavBones
        keepOffsInverts += ClavBones

    for (trgName, srcName) in boneAssoc:
        try:
            trgBone = trgRig.pose.bones[trgName]
            srcBone = srcRig.pose.bones[srcName]
        except:
            print("  -", trgName, srcName)
            continue
        boneData = CBoneData(srcBone, trgBone)
        anim.boneDatas[trgName] = boneData
        anim.boneDataList.append(boneData)
        boneData.trgRestMat = trgBone.bone.matrix_local

        boneData.trgRestInv = trgBone.bone.matrix_local.inverted()
        boneData.trgBakeMat = boneData.trgRestMat

        trgParent = None
        if trgBone.parent:  #trgBone.bone.use_inherit_rotation:
            trgParent = getParent(parAssoc[trgName], parAssoc, trgRig, anim)
            if trgParent:
                boneData.parent = anim.boneDatas[trgParent.name]
                parRest = boneData.parent.trgRestMat
                parRestInv = boneData.parent.trgRestInv
                offs = trgBone.bone.head_local - trgParent.bone.head_local
                boneData.trgOffset = parRestInv * Matrix.Translation(offs) * parRest
                boneData.trgBakeMat = parRestInv * boneData.trgRestMat


        trgRoll = utils.getRoll(trgBone.bone)
        srcRoll = source.getSourceRoll(srcName, scn) * Deg2Rad
        diff = srcRoll - trgRoll

        if srcName in keepOffsets:
            offs = trgBone.bone.matrix_local*srcBone.bone.matrix_local.inverted()
            boneData.rotOffset = boneData.trgRestInv * offs * boneData.trgRestMat
            if trgName in keepOffsInverts:
                boneData.rotOffsInv = boneData.rotOffset.inverted()
        elif abs(diff) > 0.02:
            boneData.rollMat = Matrix.Rotation(diff, 4, 'Y')
            boneData.rollInv = boneData.rollMat.inverted()

        boneData.trgBakeInv = boneData.trgBakeMat.inverted()
    return


#
#    retargetMhxRig(context, srcRig, trgRig, doFK, doIK):
#

def clearPose():
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.loc_clear()


def setupMhxAnimation(scn, srcRig, trgRig):
    clearPose()

    source.ensureSourceInited(scn)
    source.setArmature(srcRig, scn)
    target.ensureTargetInited(scn)
    print("Retarget %s --> %s" % (srcRig, trgRig))
    if trgRig.animation_data:
        trgRig.animation_data.action = None

    anim = CAnimation(srcRig, trgRig)
    (boneAssoc, parAssoc, rolls) = target.getTargetArmature(trgRig, scn)
    #(boneAssoc, ikBoneAssoc, parAssoc, rolls, mats, ikBones, ikParents) = target.makeTargetAssoc(trgRig, scn)
    setupFkBones(srcRig, trgRig, boneAssoc, parAssoc, anim, scn)
    return anim


def retargetMhxRig(context, srcRig, trgRig, doFK, doIK):
    from . import t_pose

    scn = context.scene
    utils.setMhxIk(trgRig, True, True, False)
    if scn.McpUseTPoseAsRestPose:
        scn.objects.active = trgRig
        t_pose.setTPoseAsRestPose(context)

    anim = setupMhxAnimation(scn, srcRig, trgRig)
    frames = utils.getActiveFrames(srcRig)

    scn.objects.active = trgRig
    scn.update()

    try:
        scn.frame_current = frames[0]
    except:
        raise MocapError("No frames found.")
    oldData = changeTargetData(trgRig, anim)
    clearPose()
    frameBlock = frames[0:100]
    index = 0
    first = True
    try:
        while frameBlock:
            if doFK:
                collectSrcMats(anim, frameBlock, scn)
            retargetMatrices(anim, frameBlock, first, doFK, doIK, scn)
            index += 100
            first = False
            frameBlock = frames[index:index+100]

        scn.frame_current = frames[0]
    finally:
        restoreTargetData(trgRig, oldData)

    utils.setInterpolation(trgRig)
    if doFK:
        if scn.McpAutoCorrectTPose:
            t_pose.autoCorrectFCurves(trgRig, scn)
        act = trgRig.animation_data.action
        act.name = trgRig.name[:4] + srcRig.name[2:]
        act.use_fake_user = True
        print("Retargeted %s --> %s" % (srcRig, trgRig))
    else:
        print("IK retargeted %s" % trgRig)
    return

#
#   changeTargetData(rig, anim):
#   restoreTargetData(rig, data):
#

def changeTargetData(rig, anim):
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
        rig[key+"_L"] = value
        rig[key+"_R"] = value

    layers = list(rig.data.layers)
    rig.data.layers = 32*[True]
    locks = []
    for pb in rig.pose.bones:
        constraints = []
        for cns in pb.constraints:
            if cns.type in ['LIMIT_ROTATION', 'LIMIT_SCALE']:
                constraints.append( (cns, cns.mute) )
                cns.mute = True
            elif cns.type == 'LIMIT_DISTANCE':
                cns.mute = True
        locks.append( (pb, list(pb.lock_location), list(pb.lock_rotation), list(pb.lock_scale), constraints) )
        pb.lock_location = [False, False, False]
        pb.lock_rotation = [False, False, False]
        pb.lock_scale = [False, False, False]

    norotBones = []
    """
    if mcp.target == 'MHX':
        for (name, parent) in [("UpLegRot_L", "Hip_L"), ("UpLegRot_R", "Hip_R")]:
            try:
                anim.boneDatas[parent]
                isPermanent = True
            except:
                isPermanent = False
            b = rig.data.bones[name]
            if not isPermanent:
                norotBones.append(b)
            b.use_inherit_rotation = False
    """
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
    print("Load and retarget %s" % filepath)
    time1 = time.clock()
    scn = context.scene
    (srcRig, trgRig) = load.readBvhFile(context, filepath, scn, False)
    load.renameAndRescaleBvh(context, srcRig, trgRig)
    retargetMhxRig(context, srcRig, trgRig, True, False)
    scn = context.scene
    if scn.McpDoSimplify:
        simplify.simplifyFCurves(context, trgRig, False, False)
    if scn.McpRescale:
        simplify.rescaleFCurves(context, trgRig, scn.McpRescaleFactor)
    load.deleteSourceRig(context, srcRig, 'Y_')
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
        try:
            trgRig = context.object
            scn = context.scene
            target.getTargetArmature(trgRig, scn)
            for srcRig in context.selected_objects:
                if srcRig != trgRig:
                    retargetMhxRig(context, srcRig, trgRig, True, False)
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

