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


def getVectors(rmat):
    x = Vector(rmat.col[0])
    y = Vector(rmat.col[1])
    z = Vector(rmat.col[2])
    return x,y,z


def getNewXZ(x, y):
    y.normalize()
    x -= x.dot(y)*y
    x.normalize()
    z = x.cross(y)
    return x,y,z


def matchIkLeg(legIk, toeFk, heel):
    rmat = toeFk.matrix.to_3x3()
    tHead = Vector(toeFk.matrix.col[3][:3])
    ty = rmat.col[1]
    tail = tHead + ty * toeFk.bone.length

    # 1. foot.ik is flat
    x1,y1,z1 = getVectors(rmat)
    if abs(y1[2]) > abs(z1[2]):
        y1 = -z1
    y1[2] = 0
    x1,y1,z1 = getNewXZ(x1, y1)
    head1 = tail - y1 * legIk.bone.length

    # 2. foot.ik starts at heel
    x2,y2,z2 = getVectors(rmat)
    hHead = Vector(heel.matrix.col[3][:3])
    y2 = tail - hHead
    x2,y2,z2 = getNewXZ(x2, y2)
    head2 = tail - y2 * legIk.bone.length

    # Select minimal z coordinate
    if head1[2] < head2[2]:
        x,y,z = x1,y1,z1
        head = head1
    else:
        x,y,z = x2,y2,z2
        head = head2

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


def snapIkArm(rig, snapIk, snapFk, frame):

    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk
    (uparmFk, loarmFk, elbowPtFk, handFk) = snapFk

    matchPoseTranslation(handIk, handFk)
    matchPoseRotation(handIk, handFk)
    updateScene()

    matchPoleTarget(elbowPt, uparmFk, loarmFk)

    #matchPoseRotation(uparmIk, uparmFk)
    #matchPoseRotation(loarmIk, loarmFk)


def snapIkLeg(rig, snapIk, snapFk, frame, legIkToAnkle):

    (uplegIk, lolegIk, kneePt, ankleIk, legIk, legFk, footIk, toeIk, heel) = snapIk
    (uplegFk, lolegFk, kneePtFk, footFk, toeFk) = snapFk

    if legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk)

    #matchPoseTranslation(legIk, legFk)
    #matchPoseRotation(legIk, legFk)
    matchIkLeg(legIk, toeFk, heel)
    updateScene()

    matchPoseReverse(toeIk, toeFk)
    updateScene()
    matchPoseReverse(footIk, footFk)
    updateScene()

    matchPoleTarget(kneePt, uplegFk, lolegFk)

    #matchPoseRotation(uplegIk, uplegFk)
    #matchPoseRotation(lolegIk, lolegFk)

    if not legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk)



SnapBonesAlpha8 = {
    "Arm"   : ["upper_arm", "forearm", "hand"],
    "ArmFK" : ["upper_arm.fk", "forearm.fk", "elbow.pt.fk", "hand.fk"],
    "ArmIK" : ["upper_arm.ik", "forearm.ik", None, "elbow.pt.ik", "hand.ik"],
    "Leg"   : ["thigh", "shin", "foot", "toe"],
    "LegFK" : ["thigh.fk", "shin.fk", "knee.pt.fk", "foot.fk", "toe.fk"],
    "LegIK" : ["thigh.ik", "shin.ik", "knee.pt.ik", "ankle.ik", "foot.ik", "foot_helper", "foot.rev", "toe.rev", "heel"],
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


'''
def transferToIkAtFrame(rig, frame, first):
    if mcp.target == 'MHX':


        snapIkArm(rig, lArmIkBones, lArmFkBones, "_L", frame)
        snapIkArm(rig, rArmIkBones, rArmFkBones, "_R", frame)
        snapIkLeg(rig, lLegIkBones, lLegFkBones, rig["MhaLegIkToAnkle_L"], "_L", frame, first)
        snapIkLeg(rig, rLegIkBones, rLegFkBones, rig["MhaLegIkToAnkle_R"], "_R", frame, first)

    else:
        for (ik,fk) in mcp.ikBones:
            ikPb = rig.pose.bones[ik]
            fkPb = rig.pose.bones[fk]
            matchPoseTranslation(ikPb, fkPb, frame)
            matchPoseRotation(ikPb, fkPb, frame)
'''

def clearIkAnimation(context):
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
    for bname in SnapBonesAlpha8["ArmIK"] + SnapBonesAlpha8["LegIK"]:
        if bname is not None:
            ikBones += [bname+".L", bname+".R"]

    ikFCurves = []
    for fcu in act.fcurves:
        words = fcu.data_path.split('"')
        if (words[0] == "pose.bones[" and
            words[1] in ikBones):
            ikFCurves.append(fcu)

    if ikFCurves == []:
        raise MocapError("IK bones have no animation")

    for fcu in ikFCurves:
        act.fcurves.remove(fcu)

    utils.setMhxIk(rig, False)


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

    '''
    muteConstraints(lArmCnsIk, True)
    muteConstraints(lArmCnsFk, True)
    muteConstraints(rArmCnsIk, True)
    muteConstraints(rArmCnsFk, True)
    muteConstraints(lLegCnsIk, True)
    muteConstraints(lLegCnsFk, True)
    muteConstraints(rLegCnsIk, True)
    muteConstraints(rLegCnsFk, True)
    '''

    oldLayers = list(rig.data.layers)
    utils.setMhxIk(rig, False)
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
        snapIkArm(rig, lArmSnapIk, lArmSnapFk, frame)
        snapIkArm(rig, rArmSnapIk, rArmSnapFk, frame)
        snapIkLeg(rig, lLegSnapIk, lLegSnapFk, frame, lLegIkToAnkle)
        snapIkLeg(rig, rLegSnapIk, rLegSnapFk, frame, rLegIkToAnkle)

    rig.data.layers = oldLayers
    utils.setMhxIk(rig, True)
    utils.setInterpolation(rig)

    '''
    muteConstraints(lArmCnsIk, False)
    muteConstraints(lArmCnsFk, False)
    muteConstraints(rArmCnsIk, False)
    muteConstraints(rArmCnsFk, False)
    muteConstraints(lLegCnsIk, False)
    muteConstraints(lLegCnsFk, False)
    muteConstraints(rLegCnsIk, False)
    muteConstraints(rLegCnsFk, False)
    '''


class VIEW3D_OT_TransferToIkButton(bpy.types.Operator):
    bl_idname = "mcp.transfer_to_ik"
    bl_label = "Transfer To IK Bones"
    bl_description = "Transfer FK animation to IK bones"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            transferToIk(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_ClearIkButton(bpy.types.Operator):
    bl_idname = "mcp.clear_ik_animation"
    bl_label = "Clear IK Animation"
    bl_description = "Clear Animation For IK Bones"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            clearIkAnimation(context)
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


