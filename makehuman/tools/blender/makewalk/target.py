# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; eimcp.r version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See mcp.
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
from bpy.props import *
from bpy_extras.io_utils import ExportHelper
import math
import os

from . import utils
from . import mcp
from . import t_pose
from .utils import *
from .armature import CArmature

#
#   getTargetArmature(rig, scn):
#

def getTargetArmature(rig, scn):
    selectAndSetRestPose(rig, scn)
    bones = rig.data.bones.keys()

    if scn.McpAutoTargetRig:
        name = guessTargetArmatureFromList(rig, bones, scn)
    else:
        try:
            name = scn.McpTargetRig
        except:
            raise MocapError("Initialize Target Panel first")

    if name == "Automatic":
        amt = mcp.trgArmature = CArmature()
        amt.findArmature(rig, ignoreHiddenLayers=scn.McpIgnoreHiddenLayers)
        mcp.targetArmatures["Automatic"] = amt
        scn.McpTargetRig = "Automatic"
        amt.display("Target")

        boneAssoc = []
        for pb in rig.pose.bones:
            if pb.McpBone:
                boneAssoc.append( (pb.name, pb.McpBone) )

        mcp.ikBones = []
        rig.McpTPoseFile = ""
        mcp.targetInfo[name] = (boneAssoc, mcp.ikBones, rig.McpTPoseFile)
        return boneAssoc

    else:
        scn.McpTargetRig = name
        mcp.target = name
        (boneAssoc, mcp.ikBones, rig.McpTPoseFile) = mcp.targetInfo[name]
        if not testTargetRig(name, rig, boneAssoc):
            print("WARNING:\nTarget armature %s does not match armature %s.\nBones:" % (rig.name, name))
            for pair in boneAssoc:
                print("  %s : %s" % pair)
        print("Target armature %s" % name)

        for pb in rig.pose.bones:
            pb.McpBone = pb.McpParent = ""
        for bname,mhx in boneAssoc:
            try:
                rig.pose.bones[bname].McpBone = mhx
            except KeyError:
                pass

        return boneAssoc



def guessTargetArmatureFromList(rig, bones, scn):
    ensureTargetInited(scn)
    print("Guessing target")

    if isMhxRig(rig):
        return "MHX"
    elif isRigify(rig):
        return "Rigify"
    elif False:
        for name in mcp.targetInfo.keys():
            if name not in ["MHX", "Rigify"]:
                (boneAssoc, _ikBones, _tpose) = mcp.targetInfo[name]
                if testTargetRig(name, rig, boneAssoc):
                    return name
    else:
        return "Automatic"


def testTargetRig(name, rig, rigBones):
    from .armature import validBone
    print("Testing %s" % name)
    for (bname, mhxname) in rigBones:
        try:
            pb = rig.pose.bones[bname]
        except NameError:
            pb = None
        if pb is None or not validBone(pb):
            print("  Did not find bone %s (%s)" % (bname, mhxname))
            return False
    return True

#
#   findTargetKey(mhx, list):
#

def findTargetKey(mhx, list):
    for (bone, mhx1) in list:
        if mhx1 == mhx:
            return bone
    return None

###############################################################################
#
#    Target armatures
#
###############################################################################

#    (mhx bone, text)

TargetBoneNames = [
    ('hips',         'Root bone'),
    ('spine',        'Lower spine'),
    ('spine-1',      'Middle spine'),
    ('chest',        'Upper spine'),
    ('neck',         'Neck'),
    ('head',         'Head'),
    None,
    ('clavicle.L',   'L clavicle'),
    ('deltoid.L',    'L deltoid'),
    ('upper_arm.L',  'L upper arm'),
    ('forearm.L',    'L forearm'),
    ('hand.L',       'L hand'),
    None,
    ('clavicle.R',   'R clavicle'),
    ('deltoid.R',    'R deltoid'),
    ('upper_arm.R',  'R upper arm'),
    ('forearm.R',    'R forearm'),
    ('hand.R',       'R hand'),
    None,
    ('hip.L',        'L hip'),
    ('thigh.L',      'L thigh'),
    ('shin.L',       'L shin'),
    ('foot.L',       'L foot'),
    ('toe.L',        'L toes'),
    None,
    ('hip.R',        'R hip'),
    ('thigh.R',      'R thigh'),
    ('shin.R',       'R shin'),
    ('foot.R',       'R foot'),
    ('toe.R',        'R toes'),
]

###############################################################################
#
#    Target initialization
#
###############################################################################


def loadTargets():
    mcp.targetInfo = {}

def isTargetInited(scn):
    try:
        scn.McpTargetRig
        return True
    except:
        return False


def initTargets(scn):
    mcp.targetInfo = { "Automatic" : ([], [], "") }
    mcp.targetArmatures = { "Automatic" : CArmature() }
    path = os.path.join(os.path.dirname(__file__), "target_rigs")
    for fname in os.listdir(path):
        file = os.path.join(path, fname)
        (name, ext) = os.path.splitext(fname)
        if ext == ".trg" and os.path.isfile(file):
            (name, stuff) = readTrgArmature(file, name)
            mcp.targetInfo[name] = stuff

    mcp.trgArmatureEnums =[("Automatic", "Automatic", "Automatic")]
    keys = list(mcp.targetInfo.keys())
    keys.sort()
    for key in keys:
        mcp.trgArmatureEnums.append((key,key,key))

    bpy.types.Scene.McpTargetRig = EnumProperty(
        items = mcp.trgArmatureEnums,
        name = "Target rig",
        default = 'Automatic')
    print("Defined McpTargetRig")
    return


def readTrgArmature(file, name):
    print("Read target file", file)
    fp = open(file, "r")
    status = 0
    bones = []
    tpose = ""
    ikbones = []
    for line in fp:
        words = line.split()
        if len(words) > 0:
            key = words[0].lower()
            if key[0] == "#":
                continue
            elif key == "name:":
                name = words[1]
            elif key == "bones:":
                status = 1
            elif key == "ikbones:":
                status = 2
            elif key == "t-pose:":
                status = 0
                tpose = os.path.join("target_rigs", words[1])
            elif len(words) != 2:
                print("Ignored illegal line", line)
            elif status == 1:
                bones.append( (words[0], utils.nameOrNone(words[1])) )
            elif status == 2:
                ikbones.append( (words[0], utils.nameOrNone(words[1])) )
    fp.close()
    return (name, (bones,ikbones,tpose))


def ensureTargetInited(scn):
    if not isTargetInited(scn):
        initTargets(scn)


class VIEW3D_OT_McpInitTargetsButton(bpy.types.Operator):
    bl_idname = "mcp.init_targets"
    bl_label = "Init Target Panel"
    bl_description = "(Re)load all .trg files in the target_rigs directory."
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initTargets(context.scene)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpGetTargetRigButton(bpy.types.Operator):
    bl_idname = "mcp.get_target_rig"
    bl_label = "Get Target Rig"
    bl_description = "Get the target rig type of the active armature."
    bl_options = {'UNDO'}

    def execute(self, context):
        from .retarget import changeTargetData, restoreTargetData
        rig = context.object
        data = changeTargetData(rig)
        try:
            getTargetArmature(rig, context.scene)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        finally:
            restoreTargetData(rig, data)
        return{'FINISHED'}


def saveTargetFile(filepath, context):
    from .t_pose import saveTPose

    rig = context.object
    scn = context.scene
    fname,ext = os.path.splitext(filepath)
    filepath = fname + ".trg"
    fp = open(filepath, "w")
    name = os.path.basename(fname).capitalize().replace(" ","_")
    fp.write("Name:\t%s\n\nBones:\n" % name)
    for pb in rig.pose.bones:
        if pb.McpBone:
            fp.write("\t%s\t%s\n" % (pb.name, pb.McpBone))
    fp.write("\nIkBones:\n\n")
    if scn.McpSaveTargetTPose:
        fp.write("T-pose:\t%s-tpose.json\n" % name)
    fp.close()
    print("Saved %s" % filepath)

    if scn.McpSaveTargetTPose:
        tposePath = fname + "-tpose.json"
        saveTPose(context, tposePath)


class VIEW3D_OT_McpSaveTargetFileButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mcp.save_target_file"
    bl_label = "Save Target File"
    bl_description = "Save a .trg file for this character"
    bl_options = {'UNDO'}

    filename_ext = ".trg"
    filter_glob = StringProperty(default="*.trg", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to target file", maxlen=1024, default="")

    def execute(self, context):
        try:
            saveTargetFile(self.properties.filepath, context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
