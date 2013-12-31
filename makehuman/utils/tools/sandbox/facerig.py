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


import os
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import *
from mathutils import Vector
from collections import OrderedDict

from . import io_json

#------------------------------------------------------------------------
#   Save facerig
#------------------------------------------------------------------------

def getRigAndMesh(context):
    ob = context.object
    if ob.type == 'MESH':
        return ob.parent, ob
    elif ob.type == 'ARMATURE':
        for child in ob.children:
            if child.type == 'MESH':
                return ob, child
    raise RuntimeError("An armature and a mesh must be selected")


def saveFaceRig(context, filepath):
    if os.path.splitext(filepath)[1] != ".json":
        filepath += ".json"

    rig,ob = getRigAndMesh(context)

    markers = {}
    for v in ob.data.vertices:
        for bone in rig.data.bones:
            vec = bone.head_local - v.co
            if vec.length < 1e-3:
                markers[bone.name] = [(v.index, 1.0)]
                break

    weights = {}
    vgroups = {}
    for vgrp in ob.vertex_groups:
        vgroups[vgrp.index] = vgrp
        weights[vgrp.name] = []
    for v in ob.data.vertices:
        for g in v.groups:
            vgrp = vgroups[g.group]
            weights[vgrp.name].append((v.index, g.weight))
    for vname in list(weights):
        try:
            markers[vname]
        except KeyError:
            del weights[vname]

    struct = OrderedDict()
    struct["markers"] = markers
    struct["vertex_groups"] = weights
    io_json.saveJson(struct, filepath, maxDepth=1)


class VIEW3D_OT_SaveFaceRigButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mp.save_facerig"
    bl_label = "Save Face Rig"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath the JSON file", maxlen=1024, default="")

    def execute(self, context):
        print("Saving face rig %s" % self.filepath)
        saveFaceRig(context, self.filepath)
        print("Face rig %s saved" % self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#------------------------------------------------------------------------
#   Load facerig
#------------------------------------------------------------------------

def loadFaceRig(context, filepath):
    rig,ob = getRigAndMesh(context)
    scn = context.scene
    scn.objects.active = rig
    struct = io_json.loadJson(filepath)

    # Create new bones

    bpy.ops.object.mode_set(mode='EDIT')
    parent = rig.data.edit_bones["DEF-head"]
    for bname,locs in struct["markers"].items():
        eb = rig.data.edit_bones.new(bname)
        eb.parent = parent
        eb.layers = 8*[False] + [True] + 23*[False]
        loc = Vector((0,0,0))
        for vn,w in locs:
            loc += w * ob.data.vertices[vn].co
        eb.head = loc
        eb.tail = loc + Vector((0,0.1,0))

    # Control jaw with chin and eye with

    jaw = rig.data.edit_bones["jaw"]
    djaw = rig.data.edit_bones["DEF-jaw"]
    chin = rig.data.edit_bones["m_chin"]
    jaw.layers = 15*[False] + [True] + 16*[False]
    jaw.tail = chin.head
    djaw.tail = chin.head

    leye = rig.data.edit_bones["eye.L"]
    reye = rig.data.edit_bones["eye.R"]
    head = rig.data.edit_bones["head"]
    leye.parent = head
    reye.parent = head

    bpy.ops.object.mode_set(mode='POSE')

    pjaw = rig.pose.bones["jaw"]
    pjaw.custom_shape = None
    cns = pjaw.constraints.new('STRETCH_TO')
    cns.target = rig
    cns.subtarget = chin.name
    cns.rest_length = pjaw.length

    pleye = rig.pose.bones["eye.L"]
    pleye.custom_shape = None
    cns = pleye.constraints.new('IK')
    cns.target = rig
    cns.subtarget = "L_EYE"
    cns.chain_count = 1

    preye = rig.pose.bones["eye.R"]
    preye.custom_shape = None
    cns = preye.constraints.new('IK')
    cns.target = rig
    cns.subtarget = "R_EYE"
    cns.chain_count = 1

    bpy.ops.object.mode_set(mode='OBJECT')

    # Modify weights

    sumWeights = {}
    for v in ob.data.vertices:
        sumWeights[v.index] = 0
    for vname,weights in struct["vertex_groups"].items():
        try:
            vgrp = ob.vertex_groups[vname]
        except KeyError:
            ob.vertex_groups.new(vname)
        for vn,w in weights:
            sumWeights[vn] += w

    for vn,w in sumWeights.items():
        if w > 1e-4:
            v = ob.data.vertices[vn]
            wsum = 0
            for g in v.groups:
                wsum += g.weight
            if wsum > 0:
                factor = (1-w)/wsum
                for g in v.groups:
                    g.weight *= factor

    for vname,weights in struct["vertex_groups"].items():
        for vn,w in weights:
            vgrp = ob.vertex_groups[vname]
            vgrp.add([vn], w, 'REPLACE')


class VIEW3D_OT_LoadFaceRigButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mp.load_facerig"
    bl_label = "Load Face Rig"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath the JSON file", maxlen=1024, default="")

    def execute(self, context):
        print("Loading face rig %s" % self.filepath)
        loadFaceRig(context, self.filepath)
        print("Face rig %s loaded" % self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#------------------------------------------------------------------------
#   Transfer face animation
#------------------------------------------------------------------------

def transferFaceAnim(src, trg, scn):

    # Get scale

    minvec = Vector((1e6, 1e6, 1e6))
    maxvec = Vector((-1e6, -1e6, -1e6))
    minbones = ["","",""]
    maxbones = ["","",""]
    for bone in src.data.bones:
        try:
            trg.data.bones[bone.name]
        except KeyError:
            continue
        head = bone.head_local
        vec = head - minvec
        for n in range(3):
            if vec[n] < 0:
                minvec[n] = head[n]
                minbones[n] = bone.name
        vec = head - maxvec
        for n in range(3):
            if vec[n] > 0:
                maxvec[n] = head[n]
                maxbones[n] = bone.name

    scale = Vector((1,1,1))
    svec = maxvec - minvec
    for n in range(3):
        minbone = trg.data.bones[minbones[n]]
        maxbone = trg.data.bones[maxbones[n]]
        tvec = maxbone.head_local - minbone.head_local
        scale[n] = tvec[n]/svec[n]

    print("Using scale %s" % scale)

    # Copy and scale F-curves

    sact = src.animation_data.action
    tact = bpy.data.actions.new(trg.name + "Action")
    if not trg.animation_data:
        trg.animation_data_create()
    trg.animation_data.action = tact

    for sfcu in sact.fcurves:
        bname = sfcu.data_path.split('"')[1]
        try:
            trg.data.bones[bname]
        except KeyError:
            continue
        mode = sfcu.data_path.split('.')[-1]
        if mode != "location":
            continue

        s = scale[sfcu.array_index]
        tfcu = tact.fcurves.new(sfcu.data_path, index=sfcu.array_index, action_group=bname)
        n = len(sfcu.keyframe_points)
        tfcu.keyframe_points.add(count=n)
        for i in range(n):
            t,y = sfcu.keyframe_points[i].co
            tfcu.keyframe_points[i].co = (t, s*y)


class VIEW3D_OT_TransferFaceAnimButton(bpy.types.Operator):
    bl_idname = "mp.transfer_face_anim"
    bl_label = "Transfer Face Animation"
    bl_options = {'UNDO'}

    def execute(self, context):
        src = context.object
        scn = context.scene
        for trg in scn.objects:
            if trg.select and trg != src and trg.type == 'ARMATURE':
                transferFaceAnim(src, trg, scn)
        print("Face animation transferred")
        return{'FINISHED'}
