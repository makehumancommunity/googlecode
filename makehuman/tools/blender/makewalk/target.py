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
import math
import os

from . import utils
from . import mcp
from .utils import *


def renameBone(b):
    try:
        return mcp.renames[b]
    except:
        return b

#
#   getTargetArmature(rig, scn):
#

def getTargetArmature(rig, scn):
    from . import source, t_pose

    selectAndSetRestPose(rig, scn)
    bones = rig.data.bones.keys()
    if scn.McpTargetRigMethod == 'Fixed':
        try:
            name = scn.McpTargetRig
        except:
            raise MocapError("Initialize Target Panel first")
    else:
        name = guessTargetArmatureFromList(rig, bones, scn)

    if name == "Automatic":
        amt = mcp.srcArmature = source.MocapArmature()
        amt.findArmature(rig)
        t_pose.autoTPose(rig, scn)
        mcp.targetArmatures["Automatic"] = amt
        scn.McpTargetRig = "Automatic"
        print("Target bones:")
        amt.display()

        boneAssoc = []
        for pb in rig.pose.bones:
            if pb.McpBone:
                boneAssoc.append( (pb.name, pb.McpBone) )
        parAssoc = assocParents(rig, boneAssoc, [])
        return (boneAssoc, parAssoc, None)

    scn.McpTargetRig = name
    mcp.target = name
    (boneAssoc, mcp.renames, mcp.ikBones) = mcp.targetInfo[name]
    if not testTargetRig(name, rig, boneAssoc):
        print("Bones", bones)
        raise MocapError("Target armature %s does not match armature %s" % (rig.name, name))
    print("Target armature %s" % name)
    parAssoc = assocParents(rig, boneAssoc, mcp.renames)
    return (boneAssoc, parAssoc, None)


def guessTargetArmatureFromList(rig, bones, scn):
    ensureTargetInited(scn)
    print("Guessing target")
    amtList = ["MHX", "Default"]
    for key in mcp.targetInfo.keys():
        if key not in ["MHX", "Default"]:
            amtList.append(key)
    for name in amtList:
        (boneAssoc, mcp.renames, mcp.ikBones) = mcp.targetInfo[name]
        if testTargetRig(name, rig, boneAssoc):
            return name

    if scn.McpTargetRigMethod == 'List':
        print("Bones", bones)
        raise MocapError("Did not recognize target armature %s" % rig.name)
    else:
        return "Automatic"


def assocParents(rig, boneAssoc, names):
    parAssoc = {}
    taken = [ None ]
    for (name, mhx) in boneAssoc:
        name = getName(name, names)
        pb = rig.pose.bones[name]
        pb.McpBone = mhx
        taken.append(name)
        parAssoc[name] = None
        parent = pb.parent
        while parent:
            pname = getName(parent.name, names)
            if pname in taken:
                parAssoc[name] = pname
                break
            else:
                parent = rig.pose.bones[pname].parent
    return parAssoc


def getName(name, names):
    try:
        return names[name]
    except:
        return name


def testTargetRig(name, rig, rigBones):
    print("Testing %s" % name)
    for (bname, mhxname) in rigBones:
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            pb = None
        if pb is None or not validBone(pb):
            print("Failed to find bone %s (%s)" % (bname, mhxname))
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
    ('shoulder.L',   'L clavicle'),
    ('deltoid.L',    'L deltoid'),
    ('upper_arm.L',  'L upper arm'),
    ('forearm.L',    'L forearm'),
    ('hand.L',       'L hand'),
    None,
    ('shoulder.R',   'R clavicle'),
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
    from .source import MocapArmature

    mcp.targetInfo = { "Automatic" : ([], [], []) }
    mcp.targetArmatures = { "Automatic" : MocapArmature() }
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
    renames = {}
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
            elif key == "renames:":
                status = 3
            elif len(words) != 2:
                print("Ignored illegal line", line)
            elif status == 1:
                bones.append( (words[0], utils.nameOrNone(words[1])) )
            elif status == 2:
                ikbones.append( (words[0], utils.nameOrNone(words[1])) )
            elif status == 3:
                renames[words[0]] = utils.nameOrNone(words[1])
    fp.close()
    return (name, (bones,renames,ikbones))


def ensureTargetInited(scn):
    if not isTargetInited(scn):
        initTargets(scn)


class VIEW3D_OT_McpInitTargetsButton(bpy.types.Operator):
    bl_idname = "mcp.init_targets"
    bl_label = "Init Target Panel"
    bl_options = {'UNDO'}


    def execute(self, context):
        initTargets(context.scene)
        return{'FINISHED'}
