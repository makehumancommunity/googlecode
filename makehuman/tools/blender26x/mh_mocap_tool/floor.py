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
from bpy.props import BoolProperty
from mathutils import Matrix, Vector
from .utils import MocapError
from . import utils, target, fkik


def getRigAndPlane(scn):
    rig = None
    plane = None
    for ob in scn.objects:
        if ob.select:
            if ob.type == 'ARMATURE':
                if rig:
                    raise MocapError("Two armatures selected: %s and %s" % (rig.name, ob.name))
                else:
                    rig = ob
            elif ob.type == 'MESH':
                if plane:
                    raise MocapError("Two meshes selected: %s and %s" % (plane.name, ob.name))
                else:
                    plane = ob
    if rig is None:
        raise MocapError("No rig selected")
    if plane is None:
        raise MocapError("No plane selected")
    return rig,plane


def floorFoot(context, useRight):
    scn = context.scene
    rig,plane = getRigAndPlane(scn)
    if useRight:
        ikProp = "MhaLegIk_R"
    else:
        ikProp = "MhaLegIk_L"
    try:
        useIk = rig[ikProp]
    except KeyError:
        useIk = False
    frames = utils.activeFrames(rig)
    if useIk:
        floorIkFoot(rig, plane, scn, frames, useRight)
    else:
        floorFkFoot(rig, plane, scn, frames, useRight)


def floorFkFoot(rig, plane, scn, frames, useRight):
    hipsName = target.getTrgBone("hips")
    if useRight:
        footName = target.getTrgBone("foot.R")
        toeName = target.getTrgBone("toe.R")
    else:
        footName = target.getTrgBone("foot.L")
        toeName = target.getTrgBone("toe.L")

    if hipsName is None or footName is None or toeName is None:
        raise MocapError(
            "Did not find all bones:\n" +
            "  hips: %s\n" % hips +
            "  foot: %s\n" % foot +
            "  toe: %s" % toe)

    hips = rig.pose.bones[hipsName]
    foot = rig.pose.bones[footName]
    toe = rig.pose.bones[toeName]

    for frame in frames:
        scn.frame_set(frame)
        fkik.updateScene()
        offset = 0

        toeOffset = getTailOffset(toe, plane)
        if toeOffset > offset:
            offset = toeOffset

        ballOffset = getTailOffset(foot, plane)
        if ballOffset > offset:
            offset = ballOffset

        ball = toe.matrix.col[3]
        y = toe.matrix.col[1]
        heel = ball - y*foot.length
        heelOffset = getOffset(heel, plane)
        if heelOffset > offset:
            offset = heelOffset

        print(frame, offset)
        if offset > 0:
            gmat = hips.matrix.copy()
            gmat.col[3][2] += offset
            pmat = fkik.getPoseMatrix(gmat, hips)
            fkik.insertLocation(hips, pmat)


def getOffset(point, plane):
    point3 = Vector(point[:3])
    mat = plane.matrix_world.to_3x3().normalized()
    ez = mat[2]
    vec = point3 - plane.location
    offset = -ez.dot(vec)
    return offset


def getTailOffset(bone, plane):
    head = bone.matrix.col[3]
    y = bone.matrix.col[1]
    tail = head + y*bone.length
    return getOffset(tail, plane)


class VIEW3D_OT_McpFloorFootButton(bpy.types.Operator):
    bl_idname = "mcp.floor_foot"
    bl_label = "Floor"
    bl_description = "Keep Foot Above Plane"
    bl_options = {'UNDO'}
    useRight = BoolProperty()

    def execute(self, context):
        target.getTargetArmature(context.object, context.scene)
        try:
            floorFoot(context, self.useRight)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("FK Foot raise above plane")
        return{'FINISHED'}

