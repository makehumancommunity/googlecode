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



import bpy, os
#from math import sin, cos
from mathutils import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

from . import target
from . import mcp
from . import utils
from .utils import MocapError


class MocapSourceArmature:
    def __init__(self):
        self.name = None
        self.armature = {}
        self.tposeFile = None
        self.tpose = {}


#
#    guessSrcArmature(rig, scn):
#

def guessSrcArmature(rig, scn):
    ensureSourceInited(scn)
    bestMisses = 1000
    misses = {}
    bones = rig.data.bones

    for name in mcp.sourceArmatures.keys():
        amt = mcp.sourceArmatures[name]
        nMisses = 0
        for bone in bones:
            try:
                amt.armature[canonicalSrcName(bone.name)]
            except KeyError:
                nMisses += 1
        misses[name] = nMisses
        if nMisses < bestMisses:
            best = amt
            bestMisses = nMisses

    if bestMisses == 0:
        scn.McpSourceRig = best.name
    else:
        print("Number of misses:")
        for (name, n) in misses.items():
            print("  %14s: %2d" % (name, n))
        print("Best bone map for armature %s:" % best.name)
        amt = mcp.sourceArmatures[best.name]
        for bone in bones:
            try:
                bname,_ = amt.armature[canonicalSrcName(bone.name)]
                string = "     "
            except KeyError:
                string = " *** "
                bname = "?"
            print("%s %14s => %s" % (string, bone.name, bname))
        raise MocapError('Did not find matching armature. nMisses = %d' % bestMisses)
    return best

#
#   findSrcArmature(context, rig):
#

def findSrcArmature(context, rig):
    scn = context.scene
    if scn.McpGuessSourceRig:
        mcp.srcArmature = guessSrcArmature(rig, scn)
    else:
        mcp.srcArmature = mcp.sourceArmatures[scn.McpSourceRig]
    rig.McpArmature = mcp.srcArmature.name
    print("Using matching armature %s." % rig.McpArmature)

#
#    setArmature(rig, scn)
#

def setArmature(rig, scn):
    try:
        name = rig.McpArmature
    except:
        name = scn.McpSourceRig
    if name:
        print("Setting armature to %s" % name)
        rig.McpArmature = name
        scn.McpSourceRig = name
    else:
        raise MocapError("No armature set")
    mcp.srcArmature = mcp.sourceArmatures[name]
    print("Set armature %s" % name)
    return

#
#   findSourceKey(mhx, struct):
#

def findSourceKey(bname, struct):
    for bone in struct.keys():
        (bname1, twist) = struct[bone]
        if bname == bname1:
            return (bone, twist)
    return (None, 0)


def getSourceRoll(bname, scn):
    if scn.McpAutoCorrectTPose:
        return 0
    else:
        _,roll = findSourceKey(bname, mcp.srcArmature.armature)
        return roll


def canonicalSrcName(string):
    return string.lower().replace(' ','_').replace('-','_')


###############################################################################
#
#    Source initialization
#
###############################################################################


def isSourceInited(scn):
    try:
        scn.McpSourceRig
        return True
    except:
        return False


def initSources(scn):
    mcp.sourceArmatures = {}
    path = os.path.join(os.path.dirname(__file__), "source_rigs")
    for fname in os.listdir(path):
        file = os.path.join(path, fname)
        (name, ext) = os.path.splitext(fname)
        if ext == ".src" and os.path.isfile(file):
            armature = readSrcArmature(file, name)
            print("ISS", armature)
            mcp.sourceArmatures[armature.name] = armature
    mcp.srcArmatureEnums = []
    keys = list(mcp.sourceArmatures.keys())
    keys.sort()
    for key in keys:
        mcp.srcArmatureEnums.append((key,key,key))

    bpy.types.Scene.McpSourceRig = EnumProperty(
        items = mcp.srcArmatureEnums,
        name = "Source rig",
        default = 'MB')
    scn.McpSourceRig = 'MB'
    print("Defined McpSourceRig")


def readSrcArmature(file, name):
    print("Read source file", file)
    fp = open(file, "r")
    status = 0
    armature = MocapSourceArmature()
    for line in fp:
        words = line.split()
        if len(words) > 0:
            key = words[0].lower()
            if key[0] == "#":
                continue
            elif key == "name:":
                name = armature.name = words[1]
            elif key == "armature:":
                status = 1
                amt = armature.armature
            elif key == "t-pose:":
                status = 0
                armature.tposeFile = words[1]
                print("T-pose", armature.tposeFile)
            elif len(words) < 3 or key[-1] == ":":
                print("Ignored illegal line", line)
            elif status == 1:
                for n in range(1,len(words)-2):
                    key += "_" + words[n]
                amt[canonicalSrcName(key)] = (utils.nameOrNone(words[-2]), float(words[-1]))
    fp.close()
    return armature


def ensureSourceInited(scn):
    if not isSourceInited(scn):
        initSources(scn)


class VIEW3D_OT_McpInitSourcesButton(bpy.types.Operator):
    bl_idname = "mcp.init_sources"
    bl_label = "Init Source Panel"
    bl_options = {'UNDO'}

    def execute(self, context):
        initSources(context.scene)
        return{'FINISHED'}
