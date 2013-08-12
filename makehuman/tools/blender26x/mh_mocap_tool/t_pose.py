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
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

import os
import math
from mathutils import Quaternion, Matrix
from .utils import MocapError
from .io_json import *
from . import target


def loadTPose(rig):
    filepath = os.path.join(os.path.dirname(__file__), rig.McpTPoseFile)
    struct = loadJson(filepath)

    for name,value in struct:
        print(name)
        bname = target.getTrgBone(name)
        try:
            pb = rig.pose.bones[bname]
            quat = Quaternion(value)
        except KeyError:
            quat = _UnitQuaternion
        pb.matrix_basis = quat.to_matrix().to_4x4()
        pb.McpQuatW = quat.w
        pb.McpQuatX = quat.x
        pb.McpQuatY = quat.y
        pb.McpQuatZ = quat.z

    rig.McpTPoseLoaded = True
    rig.McpRestTPose = False
    print("TPoseLoaded")


def setTPoseAsRestPose(context):
    rig = context.object
    setTPose(context)
    if not rig.McpRestTPose:
        applyRestPose(context, 1.0)
        invertQuats(rig)
        rig.McpRestTPose = True


def setDefaultPoseAsRestPose(context):
    rig = context.object
    clearTPose(context)
    if rig.McpRestTPose:
        applyRestPose(context, 0.0)
        invertQuats(rig)
        rig.McpRestTPose = False


def invertQuats(rig):
    for pb in rig.pose.bones:
        quat = Quaternion((pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ))
        pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ = quat.inverted()


def applyRestPose(context, value):
    rig = context.object
    scn = context.scene

    children = []
    for ob in scn.objects:
        if ob.type != 'MESH':
            continue

        if (ob.McpArmatureName == rig.name and
            ob.McpArmatureModifier != ""):
            mod = ob.modifiers[ob.McpArmatureModifier]
            ob.modifiers.remove(mod)
            ob.data.shape_keys.key_blocks[ob.McpArmatureModifier].value = value
            children.append(ob)
        else:
            for mod in ob.modifiers:
                if (mod.type == 'ARMATURE' and
                    mod.object == rig):
                    children.append(ob)
                    ob.McpArmatureName = rig.name
                    ob.McpArmatureModifier = mod.name
                    scn.objects.active = ob
                    bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod.name)
                    ob.data.shape_keys.key_blocks[mod.name].value = value
                    break

    scn.objects.active = rig
    bpy.ops.pose.armature_apply()
    for ob in children:
        name = ob.McpArmatureModifier
        scn.objects.active = ob
        mod = ob.modifiers.new(name, 'ARMATURE')
        mod.object = rig
        mod.use_vertex_groups = True
        bpy.ops.object.modifier_move_up(modifier=name)
        #setShapeKey(ob, name, value)

    scn.objects.active = rig
    print("Created T-pose")


def setShapeKey(ob, name, value):
    if not ob.data.shape_keys:
        return
    skey = ob.data.shape_keys.key_blocks[name]
    skey.value = value


def setTPose(context):
    rig = context.object
    if not rig.McpTPoseLoaded:
        loadTPose(rig)
    if rig.McpRestTPose:
        setRestPose(rig)
    else:
        setStoredPose(rig)
    print("Set T-pose")


def clearTPose(context):
    rig = context.object
    if not rig.McpTPoseLoaded:
        loadTPose(rig)
    if rig.McpRestTPose:
        setStoredPose(rig)
    else:
        setRestPose(rig)
    print("Cleared T-pose")


def setRestPose(rig):
    unit = Matrix()
    for pb in rig.pose.bones:
        pb.matrix_basis = unit


def setStoredPose(rig):
    for pb in rig.pose.bones:
        try:
            quat = Quaternion((pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ))
        except KeyError:
            quat = Quaternion()
        pb.matrix_basis = quat.to_matrix().to_4x4()


class VIEW3D_OT_McpRestTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_t_pose"
    bl_label = "T-pose => Rest Pose"
    bl_description = "Change rest pose to T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            target.getTargetArmature(context.object, context.scene)
            setTPoseAsRestPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpRestDefaultPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_default_pose"
    bl_label = "Default Pose => Rest Pose"
    bl_description = "Change rest pose to default pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            target.getTargetArmature(context.object, context.scene)
            setDefaultPoseAsRestPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpSetTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.set_t_pose"
    bl_label = "Set T-pose"
    bl_description = "Set pose to stored T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            target.getTargetArmature(context.object, context.scene)
            setTPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpClearTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.clear_t_pose"
    bl_label = "Clear T-pose"
    bl_description = "Clear stored T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            target.getTargetArmature(context.object, context.scene)
            clearTPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


def saveTPose(context, filepath):
    rig = context.object
    struct = []
    for pb in rig.pose.bones:
        bmat = pb.matrix
        rmat = pb.bone.matrix_local
        if pb.parent:
            bmat = pb.parent.matrix.inverted() * bmat
            rmat = pb.parent.bone.matrix_local.inverted() * rmat
        mat = rmat.inverted() * bmat
        q = mat.to_quaternion()
        magn = math.sqrt( (q.w-1)*(q.w-1) + q.x*q.x + q.y*q.y + q.z*q.z )
        if magn > 1e-4:
            struct.append((pb.name, tuple(q)))
    filepath = os.path.join(os.path.dirname(__file__), filepath)
    saveJson(struct, filepath)


class VIEW3D_OT_McpSaveTPoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.save_t_pose"
    bl_label = "Save T-pose"
    bl_description = "Save current pose as T-pose (warning: changes T-pose definition permanently)"
    bl_options = {'UNDO'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        try:
            target.getTargetArmature(context.object, context.scene)
            saveTPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Saved T-pose")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
