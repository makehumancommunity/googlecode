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

import bpy
from mathutils import Vector, Matrix
from bpy.props import *

from . import mcp, utils
from .utils import MocapError


def updateScene():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def getPoseMatrix(gmat, pb):
    restInv = pb.bone.matrix_local.inverted()
    if pb.parent:
        parInv = pb.parent.matrix.inverted()
        parRest = pb.parent.bone.matrix_local
        return restInv * (parRest * (parInv * gmat))
    else:
        return restInv * gmat


def getGlobalMatrix(mat, pb):
    gmat = pb.bone.matrix_local * mat
    if pb.parent:
        parMat = pb.parent.matrix
        parRest = pb.parent.bone.matrix_local
        return parMat * (parRest.inverted() * gmat)
    else:
        return gmat


def matchPoseTranslation(pb, src):
    pmat = getPoseMatrix(src.matrix, pb)
    insertLocation(pb, pmat)


def insertLocation(pb, mat):
    pb.location = mat.to_translation()
    pb.keyframe_insert("location", group=pb.name)


def matchPoseRotation(pb, src):
    pmat = getPoseMatrix(src.matrix, pb)
    insertRotation(pb, pmat)


def printMatrix(string,mat):
    print(string)
    for i in range(4):
        print("    %.4g %.4g %.4g %.4g" % tuple(mat[i]))


def insertRotation(pb, mat):
    q = mat.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", group=pb.name)
    else:
        pb.rotation_euler = q.to_euler(pb.rotation_mode)
        pb.keyframe_insert("rotation_euler", group=pb.name)


def matchIkLeg(legIk, toeFk, mBall, mToe, mHeel):
    rmat = toeFk.matrix.to_3x3()
    tHead = Vector(toeFk.matrix.col[3][:3])
    ty = rmat.col[1]
    tail = tHead + ty * toeFk.bone.length

    zBall = mBall.matrix.col[3][2]
    zToe = mToe.matrix.col[3][2]
    zHeel = mHeel.matrix.col[3][2]

    x = Vector(rmat.col[0])
    y = Vector(rmat.col[1])
    z = Vector(rmat.col[2])

    if zHeel > zBall and zHeel > zToe:
        # 1. foot.ik is flat
        if abs(y[2]) > abs(z[2]):
            y = -z
        y[2] = 0
    else:
        # 2. foot.ik starts at heel
        hHead = Vector(mHeel.matrix.col[3][:3])
        y = tail - hHead

    y.normalize()
    x -= x.dot(y)*y
    x.normalize()
    z = x.cross(y)
    head = tail - y * legIk.bone.length

    # Create matrix
    gmat = Matrix()
    gmat.col[0][:3] = x
    gmat.col[1][:3] = y
    gmat.col[2][:3] = z
    gmat.col[3][:3] = head
    pmat = getPoseMatrix(gmat, legIk)

    insertLocation(legIk, pmat)
    insertRotation(legIk, pmat)


def matchPoleTarget(pb, above, below):
    x = Vector(above.matrix.col[1][:3])
    y = Vector(below.matrix.col[1][:3])
    p0 = Vector(below.matrix.col[3][:3])
    n = x.cross(y)
    if abs(n.length) > 1e-4:
        z = x - y
        n.normalize()
        z -= z.dot(n)*n
        z.normalize()
        p = p0 + 3.0*z
    else:
        p = p0
    gmat = Matrix.Translation(p)
    pmat = getPoseMatrix(gmat, pb)
    insertLocation(pb, pmat)


def matchPoseReverse(pb, src):
    gmat = src.matrix
    tail = gmat.col[3] + src.length * gmat.col[1]
    rmat = Matrix((gmat.col[0], -gmat.col[1], -gmat.col[2], tail))
    rmat.transpose()
    pmat = getPoseMatrix(rmat, pb)
    pb.matrix_basis = pmat
    insertRotation(pb, pmat)


def matchPoseScale(pb, src):
    pmat = getPoseMatrix(src.matrix, pb)
    pb.scale = pmat.to_scale()
    pb.keyframe_insert("scale", group=pb.name)


def snapFkArm(rig, snapIk, snapFk, frame):

    (uparmFk, loarmFk, handFk) = snapFk
    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk

    matchPoseRotation(uparmFk, uparmIk)
    matchPoseRotation(loarmFk, loarmIk)
    matchPoseRotation(handFk, handIk)


def snapIkArm(rig, snapIk, snapFk, frame):

    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk
    (uparmFk, loarmFk, handFk) = snapFk

    matchPoseTranslation(handIk, handFk)
    matchPoseRotation(handIk, handFk)
    updateScene()

    matchPoleTarget(elbowPt, uparmFk, loarmFk)

    #matchPoseRotation(uparmIk, uparmFk)
    #matchPoseRotation(loarmIk, loarmFk)


def snapFkLeg(rig, snapIk, snapFk, frame, legIkToAnkle):

    (uplegIk, lolegIk, kneePt, ankleIk, legIk, footRev, toeRev, mBall, mToe, mHeel) = snapIk
    (uplegFk, lolegFk, footFk, toeFk) = snapFk

    matchPoseRotation(uplegFk, uplegIk)
    matchPoseRotation(lolegFk, lolegIk)
    if not legIkToAnkle:
        matchPoseReverse(footFk, footRev)
        matchPoseReverse(toeFk, toeRev)


def snapIkLeg(rig, snapIk, snapFk, frame, legIkToAnkle):

    (uplegIk, lolegIk, kneePt, ankleIk, legIk, footRev, toeRev, mBall, mToe, mHeel) = snapIk
    (uplegFk, lolegFk, footFk, toeFk) = snapFk

    if legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk)

    #matchPoseTranslation(legIk, legFk)
    #matchPoseRotation(legIk, legFk)
    matchIkLeg(legIk, toeFk, mBall, mToe, mHeel)
    updateScene()

    matchPoseReverse(toeRev, toeFk)
    updateScene()
    matchPoseReverse(footRev, footFk)
    updateScene()

    matchPoleTarget(kneePt, uplegFk, lolegFk)

    #matchPoseRotation(uplegIk, uplegFk)
    #matchPoseRotation(lolegIk, lolegFk)

    if not legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk)



SnapBonesAlpha8 = {
    "Arm"   : ["upper_arm", "forearm", "hand"],
    "ArmFK" : ["upper_arm.fk", "forearm.fk", "hand.fk"],
    "ArmIK" : ["upper_arm.ik", "forearm.ik", None, "elbow.pt.ik", "hand.ik"],
    "Leg"   : ["thigh", "shin", "foot", "toe"],
    "LegFK" : ["thigh.fk", "shin.fk", "foot.fk", "toe.fk"],
    "LegIK" : ["thigh.ik", "shin.ik", "knee.pt.ik", "ankle.ik", "foot.ik", "foot.rev", "toe.rev", "ball.marker", "toe.marker", "heel.marker"],
}

def getSnapBones(rig, key, suffix):
    try:
        rig.pose.bones["thigh.fk.L"]
        names = SnapBonesAlpha8[key]
        suffix = '.' + suffix[1:]
    except KeyError:
        names = None
    if not names:
        raise NameError("Not an mhx armature")

    pbones = []
    constraints = []
    for name in names:
        if name:
            pb = rig.pose.bones[name+suffix]
            pbones.append(pb)
            for cns in pb.constraints:
                if cns.type == 'LIMIT_ROTATION' and not cns.mute:
                    constraints.append(cns)
        else:
            pbones.append(None)
    return tuple(pbones),constraints


def muteConstraints(constraints, value):
    for cns in constraints:
        cns.mute = value


def clearAnimation(context, type):
    from . import target

    rig = context.object
    if not rig.animation_data:
        raise MocapError("Rig has no animation data")
    act = rig.animation_data.action
    if not act:
        raise MocapError("Rig has no action")

    scn = context.scene
    target.getTargetArmature(rig, scn)

    ikBones = []
    if scn.McpFkIkArms:
        for bname in SnapBonesAlpha8["Arm" + type]:
            if bname is not None:
                ikBones += [bname+".L", bname+".R"]
    if scn.McpFkIkLegs:
        for bname in SnapBonesAlpha8["Leg" + type]:
            if bname is not None:
                ikBones += [bname+".L", bname+".R"]

    ikFCurves = []
    for fcu in act.fcurves:
        words = fcu.data_path.split('"')
        if (words[0] == "pose.bones[" and
            words[1] in ikBones):
            ikFCurves.append(fcu)

    if ikFCurves == []:
        raise MocapError("%s bones have no animation" % type)

    for fcu in ikFCurves:
        act.fcurves.remove(fcu)

    utils.setMhxIk(rig, scn.McpFkIkArms, scn.McpFkIkLegs, (type=="FK"))


def transferToFk(context):
    from . import target

    rig = context.object
    scn = context.scene
    if not utils.isMhxRig(rig):
        raise MocapError("Can only transfer to FK with MHX rig")
    target.getTargetArmature(rig, scn)

    lArmSnapIk,lArmCnsIk = getSnapBones(rig, "ArmIK", "_L")
    lArmSnapFk,lArmCnsFk = getSnapBones(rig, "ArmFK", "_L")
    rArmSnapIk,rArmCnsIk = getSnapBones(rig, "ArmIK", "_R")
    rArmSnapFk,rArmCnsFk = getSnapBones(rig, "ArmFK", "_R")
    lLegSnapIk,lLegCnsIk = getSnapBones(rig, "LegIK", "_L")
    lLegSnapFk,lLegCnsFk = getSnapBones(rig, "LegFK", "_L")
    rLegSnapIk,rLegCnsIk = getSnapBones(rig, "LegIK", "_R")
    rLegSnapFk,rLegCnsFk = getSnapBones(rig, "LegFK", "_R")

    #muteAllConstraints(rig, True)

    oldLayers = list(rig.data.layers)
    utils.setMhxIk(rig, scn.McpFkIkArms, scn.McpFkIkLegs, True)
    rig.data.layers = 14*[True] + 2*[False] + 14*[True] + 2*[False]

    lLegIkToAnkle = rig["MhaLegIkToAnkle_L"]
    rLegIkToAnkle = rig["MhaLegIkToAnkle_R"]

    frames = utils.getActiveFramesBetweenMarkers(rig, scn)
    for n,frame in enumerate(frames):
        if n%10 == 0:
            print(frame)
        scn.frame_set(frame)
        updateScene()
        if scn.McpFkIkArms:
            snapFkArm(rig, lArmSnapIk, lArmSnapFk, frame)
            snapFkArm(rig, rArmSnapIk, rArmSnapFk, frame)
        if scn.McpFkIkLegs:
            snapFkLeg(rig, lLegSnapIk, lLegSnapFk, frame, lLegIkToAnkle)
            snapFkLeg(rig, rLegSnapIk, rLegSnapFk, frame, rLegIkToAnkle)

    rig.data.layers = oldLayers
    utils.setMhxIk(rig, scn.McpFkIkArms, scn.McpFkIkLegs, False)
    utils.setInterpolation(rig)
    #muteAllConstraints(rig, False)


def transferToIk(context):
    from . import target

    rig = context.object
    scn = context.scene
    if not utils.isMhxRig(rig):
        raise MocapError("Can only transfer to IK with MHX rig")
    target.getTargetArmature(rig, scn)

    lArmSnapIk,lArmCnsIk = getSnapBones(rig, "ArmIK", "_L")
    lArmSnapFk,lArmCnsFk = getSnapBones(rig, "ArmFK", "_L")
    rArmSnapIk,rArmCnsIk = getSnapBones(rig, "ArmIK", "_R")
    rArmSnapFk,rArmCnsFk = getSnapBones(rig, "ArmFK", "_R")
    lLegSnapIk,lLegCnsIk = getSnapBones(rig, "LegIK", "_L")
    lLegSnapFk,lLegCnsFk = getSnapBones(rig, "LegFK", "_L")
    rLegSnapIk,rLegCnsIk = getSnapBones(rig, "LegIK", "_R")
    rLegSnapFk,rLegCnsFk = getSnapBones(rig, "LegFK", "_R")

    #muteAllConstraints(rig, True)

    oldLayers = list(rig.data.layers)
    utils.setMhxIk(rig, scn.McpFkIkArms, scn.McpFkIkLegs, False)
    rig.data.layers = 14*[True] + 2*[False] + 14*[True] + 2*[False]

    lLegIkToAnkle = rig["MhaLegIkToAnkle_L"]
    rLegIkToAnkle = rig["MhaLegIkToAnkle_R"]

    frames = utils.getActiveFramesBetweenMarkers(rig, scn)
    #frames = range(scn.frame_start, scn.frame_end+1)
    for n,frame in enumerate(frames):
        if n%10 == 0:
            print(frame)
        scn.frame_set(frame)
        updateScene()
        if scn.McpFkIkArms:
            snapIkArm(rig, lArmSnapIk, lArmSnapFk, frame)
            snapIkArm(rig, rArmSnapIk, rArmSnapFk, frame)
        if scn.McpFkIkLegs:
            snapIkLeg(rig, lLegSnapIk, lLegSnapFk, frame, lLegIkToAnkle)
            snapIkLeg(rig, rLegSnapIk, rLegSnapFk, frame, rLegIkToAnkle)

    rig.data.layers = oldLayers
    utils.setMhxIk(rig, scn.McpFkIkArms, scn.McpFkIkLegs, True)
    utils.setInterpolation(rig)
    #muteAllConstraints(rig, False)


def muteAllConstraints(rig, value):
    lArmSnapIk,lArmCnsIk = getSnapBones(rig, "ArmIK", "_L")
    lArmSnapFk,lArmCnsFk = getSnapBones(rig, "ArmFK", "_L")
    rArmSnapIk,rArmCnsIk = getSnapBones(rig, "ArmIK", "_R")
    rArmSnapFk,rArmCnsFk = getSnapBones(rig, "ArmFK", "_R")
    lLegSnapIk,lLegCnsIk = getSnapBones(rig, "LegIK", "_L")
    lLegSnapFk,lLegCnsFk = getSnapBones(rig, "LegFK", "_L")
    rLegSnapIk,rLegCnsIk = getSnapBones(rig, "LegIK", "_R")
    rLegSnapFk,rLegCnsFk = getSnapBones(rig, "LegFK", "_R")

    muteConstraints(lArmCnsIk, value)
    muteConstraints(lArmCnsFk, value)
    muteConstraints(rArmCnsIk, value)
    muteConstraints(rArmCnsFk, value)
    muteConstraints(lLegCnsIk, value)
    muteConstraints(lLegCnsFk, value)
    muteConstraints(rLegCnsIk, value)
    muteConstraints(rLegCnsFk, value)


class VIEW3D_OT_TransferToFkButton(bpy.types.Operator):
    bl_idname = "mcp.transfer_to_fk"
    bl_label = "Transfer IK => FK"
    bl_description = "Transfer IK animation to FK bones"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            transferToFk(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_TransferToIkButton(bpy.types.Operator):
    bl_idname = "mcp.transfer_to_ik"
    bl_label = "Transfer FK => IK"
    bl_description = "Transfer FK animation to IK bones"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            transferToIk(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_ClearAnimationButton(bpy.types.Operator):
    bl_idname = "mcp.clear_animation"
    bl_label = "Clear Animation"
    bl_description = "Clear Animation For FK or IK Bones"
    bl_options = {'UNDO'}
    type = StringProperty()

    def execute(self, context):
        try:
            clearAnimation(context, self.type)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


def printHand(context):
        rig = context.object
        '''
        handFk = rig.pose.bones["hand.fk.L"]
        handIk = rig.pose.bones["hand.ik.L"]
        print(handFk)
        print(handFk.matrix)
        print(handIk)
        print(handIk.matrix)
        '''
        footIk = rig.pose.bones["foot.ik.L"]
        print(footIk)
        print(footIk.matrix)


class VIEW3D_OT_PrintHandsButton(bpy.types.Operator):
    bl_idname = "mcp.print_hands"
    bl_label = "Print Hands"
    bl_options = {'UNDO'}

    def execute(self, context):
        printHand(context)
        return{'FINISHED'}


