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
import os
from collections import OrderedDict
from math import pi
from mathutils import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

from . import target
from . import mcp
from .utils import *


class MocapArmature:

    def __init__(self):
        self.name = "Automatic"
        self.boneNames = OrderedDict()
        self.tposeFile = None


    def display(self):
        print("Source Armature", self.name)
        for bname,value in self.boneNames.items():
            print("  %14s %14s" % (bname, value[0]))


    def findArmature(self, rig):
        for pb in rig.pose.bones:
            if pb.parent is None:
                hips = pb
                break

        hipsChildren = validChildren(hips)
        while (len(hipsChildren) < 3):
            hips = hipsChildren[0]
            if len(hipsChildren) == 2:
                hipname = hips.name.lower()
                for string in ["foot", "hand", "leg", "arm"]:
                    if string in hipname:
                        hips = hipsChildren[1]
                        break
            hipsChildren = validChildren(hips)

        self.setBone("hips", hips)
        hiphead,hiptail,_ = getHeadTailDir(hips)

        # Reversed hip
        if False and len(hipsChildren) == 2:
            legroot = hipsChildren[1]
            spine = hipsChildren[0]
            _,terminal = chainEnd(legroot)
            head,tail,vec = getHeadTailDir(terminal)
            if tail[2] > hiptail[2]:
                legroot = hipsChildren[0]
                spine = hipsChildren[1]
            hipsChildren = [spine] + validChildren(legroot)

        if len(hipsChildren) < 3:
            string = "Hips %s has %d children:\n" % (hips.name, len(hipsChildren))
            for child in hipsChildren:
                string += "  %s\n" % child.name
            raise MocapError(string)

        spine = None
        spineTail = hiptail
        leftLeg = None
        leftLegTail = hiptail
        rightLeg = None
        rightLegTail = hiptail

        for pb in hipsChildren:
            _,terminal = chainEnd(pb)
            head,tail,vec = getHeadTailDir(terminal)
            if tail[2] > spineTail[2]:
                spine = pb
                spineTail = tail
            elif tail[2] < leftLegTail[2] and tail[0] > hiptail[0]:
                leftLeg = pb
                leftLegTail = tail
            elif tail[2] < rightLegTail[2] and tail[0] < hiptail[0]:
                rightLeg = pb
                rightLegTail = tail
            elif len(hipsChildren) == 3:
                print("Terminal", terminal)
                print("  ", tail)

        if (spine is None) or (leftLeg is None) or (rightLeg is None):
            string = "Did not find all limbs emanating from hips:\n"
            string += self.errLimb("spine", spine, spineTail)
            string += self.errLimb("left leg", leftLeg, leftLegTail)
            string += self.errLimb("right leg", rightLeg, rightLegTail)
            raise MocapError(string)

        self.findSpine(spine)
        self.findLeg(leftLeg, ".L")
        self.findLeg(rightLeg, ".R")


    def errLimb(self, name, pb, tail):
        if pb is None:
            return ("  No %s\n" % name)
        else:
            return ("  %s = %s, tail = %s\n" % (name, pb.name, tuple(tail)))


    def setBone(self, bname, pb):
        pb.McpBone = bname
        try:
            tpose = TPose[bname]
        except:
            tpose = None
        if tpose is None:
            roll = 0
        else:
            _,_,vec = getHeadTailDir(pb)
            #roll = math.acos(vec.dot(tpose))
            roll = 0
        self.boneNames[canonicalSrcName(pb.name)] = (bname, roll*Rad2Deg)


    def findTerminal(self, pb, bnames):
        self.setBone(bnames[0], pb)
        bnames = bnames[1:]
        children = validChildren(pb)
        if bnames and len(children) == 1:
            return self.findTerminal(children[0], bnames)
        else:
            while len(children) == 1:
                pb = children[0]
                children = validChildren(pb)
            return pb


    def findLeg(self, thigh, suffix):
        bnames = ["thigh"+suffix, "shin"+suffix, "foot"+suffix, "toe"+suffix]
        shin = validChildren(thigh)[0]
        foot = validChildren(shin)[0]
        if thigh.bone.length < foot.bone.length:
            self.findTerminal(shin, bnames)
        else:
            self.findTerminal(thigh, bnames)


    def findArm(self, shoulder, suffix):
        bnames = ["clavicle"+suffix, "upper_arm"+suffix, "forearm"+suffix, "hand"+suffix]
        upperarm = validChildren(shoulder)[0]
        forearm = validChildren(upperarm)[0]
        hand = validChildren(forearm)[0]
        if upperarm.bone.length < hand.bone.length:
            bnames = [bnames[0], "deltoid"+suffix] + bnames[1:]
        self.findTerminal(shoulder, bnames)


    def findHead(self, neck):
        bnames = ["neck", "head"]
        self.findTerminal(neck, bnames)


    def findSpine(self, spine1):
        n,spine2 = chainEnd(spine1)
        if n == 1:
            bnames = ["spine"]
        elif n == 2:
            bnames = ["spine", "chest"]
        elif n == 3:
            bnames = ["spine", "spine-1", "chest"]
        else:
            bnames = ["spine", "spine-1", "chest", "chest-1"]

        self.findTerminal(spine1, bnames)
        spine2Children = validChildren(spine2)
        if len(spine2Children) == 3:
            _,stail,_ = getHeadTailDir(spine2)
            limbs = []
            for pb in spine2Children:
                _,tail,_ = getHeadTailDir(pb)
                limbs.append((tail[0],pb))
            limbs.sort()
            self.findArm(limbs[0][1], ".R")
            self.findHead(limbs[1][1])
            self.findArm(limbs[2][1], ".L")
        else:
            string = ("Top of spine %s has %d children:\n" % (spine2.name, len(spine2Children)))
            for child in spine2Children:
                string += "  %s\n" % child.name
            raise MocapError(string)

def validChildren(pb):
    children = []
    for child in pb.children:
        if validBone(child):
            children.append(child)
    return children


def chainEnd(pb):
    n = 1
    while pb and (len(validChildren(pb)) == 1):
        n += 1
        pb = validChildren(pb)[0]
    return n,pb


def getHeadTailDir(pb):
    mat = pb.bone.matrix_local
    head = Vector(mat.col[3][:3])
    vec = Vector(mat.col[1][:3])
    tail = head + pb.bone.length * vec
    return head, tail, vec

#
#    guessSrcArmatureFromList(rig, scn):
#

def guessSrcArmatureFromList(rig, scn):
    ensureSourceInited(scn)
    bestMisses = 1000

    misses = {}
    for name in mcp.sourceArmatures.keys():
        if name == "Automatic":
            continue
        amt = mcp.sourceArmatures[name]
        nMisses = 0
        for bone in rig.data.bones:
            try:
                amt.boneNames[canonicalSrcName(bone.name)]
            except KeyError:
                nMisses += 1
        misses[name] = nMisses
        if nMisses < bestMisses:
            best = amt
            bestMisses = nMisses

    if bestMisses == 0:
        scn.McpSourceRig = best.name
        return best
    else:
        print("Number of misses:")
        for (name, n) in misses.items():
            print("  %14s: %2d" % (name, n))
        print("Best bone map for armature %s:" % best.name)
        amt = mcp.sourceArmatures[best.name]
        for bone in rig.data.bones:
            try:
                bname,_ = amt.boneNames[canonicalSrcName(bone.name)]
                string = "     "
            except KeyError:
                string = " *** "
                bname = "?"
            print("%s %14s => %s" % (string, bone.name, bname))
        raise MocapError('Did not find matching armature. nMisses = %d' % bestMisses)

#
#   findSrcArmature(context, rig):
#

def findSrcArmature(context, rig):
    from . import t_pose
    scn = context.scene

    if scn.McpSourceRigMethod == 'Fixed':
        mcp.srcArmature = mcp.sourceArmatures[scn.McpSourceRig]
    elif scn.McpSourceRigMethod == 'List':
        mcp.srcArmature = guessSrcArmatureFromList(rig, scn)
    elif scn.McpSourceRigMethod == 'Auto':
        amt = mcp.srcArmature = MocapArmature()
        selectAndSetRestPose(rig, scn)
        amt.findArmature(rig)
        t_pose.autoTPose(rig, scn)
        mcp.sourceArmatures["Automatic"] = amt
        amt.display()

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
        (bname1, roll) = struct[bone]
        if bname == bname1:
            return (bone, roll)
    return (None, 0)


def getSourceRoll(bname, scn):
    if scn.McpAutoCorrectTPose:
        return 0
    else:
        _,roll = findSourceKey(bname, mcp.srcArmature.boneNames)
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
    mcp.sourceArmatures = { "Automatic" : MocapArmature() }
    path = os.path.join(os.path.dirname(__file__), "source_rigs")
    for fname in os.listdir(path):
        file = os.path.join(path, fname)
        (name, ext) = os.path.splitext(fname)
        if ext == ".src" and os.path.isfile(file):
            armature = readSrcArmature(file, name)
            mcp.sourceArmatures[armature.name] = armature
    mcp.srcArmatureEnums = [("Automatic", "Automatic", "Automatic")]
    keys = list(mcp.sourceArmatures.keys())
    keys.sort()
    for key in keys:
        mcp.srcArmatureEnums.append((key,key,key))

    bpy.types.Scene.McpSourceRig = EnumProperty(
        items = mcp.srcArmatureEnums,
        name = "Source rig",
        default = 'Automatic')
    scn.McpSourceRig = 'Automatic'
    print("Defined McpSourceRig")


def readSrcArmature(file, name):
    print("Read source file", file)
    fp = open(file, "r")
    status = 0
    armature = MocapArmature()
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
                amt = armature.boneNames
            elif key == "t-pose:":
                status = 0
                armature.tposeFile = os.path.join("source_rigs", words[1])
            elif len(words) < 3 or key[-1] == ":":
                print("Ignored illegal line", line)
            elif status == 1:
                for n in range(1,len(words)-2):
                    key += "_" + words[n]
                amt[canonicalSrcName(key)] = (nameOrNone(words[-2]), float(words[-1]))
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
