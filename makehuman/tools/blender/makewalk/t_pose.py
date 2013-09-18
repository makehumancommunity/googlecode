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
from . import mcp, utils
from .utils import *
from .io_json import *


def setTPoseAsRestPose(context):
    rig = context.object
    setTPose(rig)
    if not rig.McpRestTPose:
        applyRestPose(context, 1.0)
        invertQuats(rig)
        rig.McpRestTPose = True


def setDefaultPoseAsRestPose(context):
    rig = context.object
    clearTPose(rig)
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

        scn.objects.active = ob
        if ob != context.object:
            raise StandardError("Context switch did not take:\nob = %s\nc.ob = %s\nc.aob = %s" %
                (ob, context.object, context.active_object))

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
                    bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod.name)
                    ob.data.shape_keys.key_blocks[mod.name].value = value
                    ob.McpArmatureName = rig.name
                    ob.McpArmatureModifier = mod.name
                    break

    scn.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
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


def setTPose(rig):
    if not rig.McpTPoseLoaded:
        loadTPose(rig)
    if rig.McpRestTPose:
        setRestPose(rig)
    else:
        setStoredPose(rig)
    print("Set T-pose")


def clearTPose(rig):
    if not rig.McpTPoseLoaded:
        loadTPose(rig)
    if rig.McpRestTPose:
        setStoredPose(rig)
    else:
        setRestPose(rig)
    print("Cleared T-pose")


def setStoredPose(rig):
    for pb in rig.pose.bones:
        try:
            quat = Quaternion((pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ))
        except KeyError:
            quat = Quaternion()
        pb.matrix_basis = quat.to_matrix().to_4x4()


def addTPoseAtFrame0(rig, scn):
    scn.frame_current = 0
    if rig.McpTPoseLoaded:
        setTPose(rig)
    elif mcp.srcArmature.tposeFile:
        rig.McpTPoseFile = os.path.join("source_rigs", mcp.srcArmature.tposeFile)
        setTPose(rig)
    else:
        setRestPose(rig)
    for pb in rig.pose.bones:
        if pb.rotation_mode == 'QUATERNION':
            pb.keyframe_insert('rotation_quaternion')
        else:
            pb.keyframe_insert('rotation_euler')


def autoCorrectFCurves(rig, scn):
    from . import loop
    scn.frame_current = 0
    scn.objects.active = rig
    setTPose(rig)
    for pb in rig.pose.bones:
        pb.bone.select = True
    loop.shiftBoneFCurves(rig, scn)


class VIEW3D_OT_McpRestTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_t_pose"
    bl_label = "T-pose => Rest Pose"
    bl_description = "Change rest pose to T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initRig(context)
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
            initRig(context)
            setDefaultPoseAsRestPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpRestCurrentPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_current_pose"
    bl_label = "Current Pose => Rest Pose"
    bl_description = "Change rest pose to current pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initRig(context)
            applyRestPose(context, 1.0)
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
            initRig(context)
            setTPose(context.object)
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
            initRig(context)
            clearTPose(context.object)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


def loadTPose(rig):
    filepath = os.path.join(os.path.dirname(__file__), rig.McpTPoseFile)
    filepath = os.path.normpath(filepath)
    print("Loading %s" % filepath)
    struct = loadJson(filepath)

    for name,value in struct:
        bname = getBoneName(rig, name)
        print("  ", name, bname)
        try:
            pb = rig.pose.bones[bname]
            quat = Quaternion(value)
        except:
            quat = Quaternion()
        pb.matrix_basis = quat.to_matrix().to_4x4()
        setBoneTPose(pb, quat)

    rig.McpTPoseLoaded = True
    rig.McpRestTPose = False
    print("TPoseLoaded")


def setBoneTPose(pb, quat):
    pb.McpQuatW = quat.w
    pb.McpQuatX = quat.x
    pb.McpQuatY = quat.y
    pb.McpQuatZ = quat.z


class VIEW3D_OT_McpLoadTPoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_t_pose"
    bl_label = "Load T-pose"
    bl_description = "Load T-pose to active rig"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to tpose file", maxlen=1024, default="")

    def execute(self, context):
        initRig(context)
        rig = context.object
        rig.McpTPoseFile = os.path.relpath(self.filepath, os.path.dirname(__file__))
        try:
            loadTPose(rig)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Loaded T-pose")
        setTPose(rig)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


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
    print("Saving %s" % filepath)
    saveJson(struct, filepath)


class VIEW3D_OT_McpSaveTPoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.save_t_pose"
    bl_label = "Save T-pose"
    bl_description = "Save current pose as T-pose"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to tpose file", maxlen=1024, default="")

    def execute(self, context):
        try:
            saveTPose(context, self.filepath)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Saved T-pose")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def initRig(context):
    from . import target
    from . import source
    rig = context.object
    if rig.McpIsSourceRig:
        source.findSrcArmature(context, rig)
    else:
        target.getTargetArmature(rig, context.scene)


def getBoneName(rig, name):
    if rig.McpIsSourceRig:
        return name
    else:
        pb = utils.getTrgBone(name, rig)
        return pb.name

