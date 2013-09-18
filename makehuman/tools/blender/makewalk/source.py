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
import math
from mathutils import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

from . import target
from . import mcp
from .utils import *


EX1 = Matrix.Rotation(math.pi/2, 4, 'Z')
EX2 = Matrix.Rotation(-math.pi/2, 4, 'Z')
EZ1 = Matrix.Rotation(math.pi/2, 4, 'X')
EZ2 = Matrix.Rotation(-math.pi/2, 4, 'X')
Zero = Vector((0,0,0))

TPose = {
    "upper_arm.L" : EX2,
    "upper_arm.R" : EX1,
    "forearm.L" :   EX2,
    "forearm.R" :   EX1,

    "thigh.L" :     EZ2,
    "thigh.R" :     EZ2,
    "shin.L" :      EZ2,
    "shin.R" :      EZ2,
}


class MocapSourceArmature:

    def __init__(self):
        self.name = "Automatic"
        self.boneNames = OrderedDict()
        self.tposeFile = None


    def display(self):
        print("Source Armature", self.name)
        for bname,value in self.boneNames.items():
            print("  %14s %14s" % (bname, value[0]))


    def correctTPose(self, rig, scn):
        from .t_pose import setBoneTPose

        scn.objects.active = rig
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.loc_clear()

        return

        fixBones = []
        for pb in rig.pose.bones:
            print("  ", pb.name, pb.McpBone)
            try:
                fixBones.append( (pb, TPose[pb.McpBone]) )
            except KeyError:
                pass

        for pb,ey in fixBones:
            mat = ey.copy()
            mat.col[3] = pb.matrix.col[3]
            loc = pb.bone.matrix_local
            if pb.parent:
                mat = pb.parent.matrix.inverted() * mat
                loc = pb.parent.bone.matrix_local.inverted() * loc
            mat =  loc.inverted() * mat
            euler = mat.to_euler()
            euler.y = 0
            pb.matrix_basis = euler.to_matrix().to_4x4()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='POSE')

            quat = pb.matrix_basis.to_quaternion()
            setBoneTPose(pb, quat)

        rig.McpTPoseLoaded = True
        rig.McpRestTPose = False


    def findArmature(self, rig):
        for pb in rig.pose.bones:
            if pb.parent is None:
                hips = pb
                break

        while (len(hips.children) == 1):
            hips = hips.children[0]

        if len(hips.children) < 3:
            raise MocapError("Hips has %d children" % len(hips.children))

        hips.McpBone = "hips"
        self.setBone("hips", hips)
        hiphead,hiptail,_ = getHeadTailDir(hips)

        spine = None
        spineTail = Zero
        leftLeg = None
        leftLegTail = Zero
        rightLeg = None
        rightLegTail = Zero

        for pb in hips.children:
            _,terminal = chainEnd(pb)
            head,tail,vec = getHeadTailDir(terminal)
            if tail[2] > spineTail[2]:
                spine = pb
                spineTail = tail
            elif tail[2] < leftLegTail[2] and tail[0] > 0:
                leftLeg = pb
                leftLegTail = tail
            elif tail[2] < rightLegTail[2] and tail[0] < 0:
                rightLeg = pb
                rightLegTail = tail

        if (spine is None) or (leftLeg is None) or (rightLeg is None):
            raise MocapError("Did not find all limbs:\nspine = %s\nleftLeg = %s\nrightLeg = %s" %
                (spine, leftLeg, rightLeg))

        self.findSpine(spine)
        self.findLeg(leftLeg, ".L")
        self.findLeg(rightLeg, ".R")


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
        if bnames and len(pb.children) == 1:
            return self.findTerminal(pb.children[0], bnames)
        else:
            while len(pb.children) == 1:
                pb = pb.children[0]
            return pb


    def findLeg(self, thigh, suffix):
        bnames = ["thigh"+suffix, "shin"+suffix, "foot"+suffix, "toe"+suffix]
        shin = thigh.children[0]
        foot = shin.children[0]
        if thigh.bone.length < foot.bone.length:
            self.findTerminal(shin, bnames)
        else:
            self.findTerminal(thigh, bnames)


    def findArm(self, shoulder, suffix):
        bnames = ["clavicle"+suffix, "upper_arm"+suffix, "forearm"+suffix, "hand"+suffix]
        upperarm = shoulder.children[0]
        forearm = upperarm.children[0]

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
        if len(spine2.children) == 3:
            _,stail,_ = getHeadTailDir(spine2)
            for pb in spine2.children:
                _,terminal = chainEnd(pb)
                _,tail,vec = getHeadTailDir(terminal)
                if vec[2] > 0 and abs(vec[0]) < 0.1:
                    self.findHead(pb)
                elif tail[0] > stail[0]:
                    self.findArm(pb, ".L")
                elif tail[0] < stail[0]:
                    self.findArm(pb, ".R")


def chainEnd(pb):
    n = 1
    while pb and (len(pb.children) == 1):
        n += 1
        pb = pb.children[0]
    return n,pb


def getHeadTailDir(pb):
    mat = pb.bone.matrix_local
    head = Vector(mat.col[3][:3])
    vec = Vector(mat.col[1][:3])
    tail = head + pb.bone.length * vec
    return head, tail, vec

#
#    guessSrcArmature(rig, scn):
#

def guessSrcArmature(rig, scn):
    ensureSourceInited(scn)
    bestMisses = 1000
    misses = {}
    bones = rig.data.bones

    for name in mcp.sourceArmatures.keys():
        if name == "Automatic":
            continue
        amt = mcp.sourceArmatures[name]
        nMisses = 0
        for bone in bones:
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
        amt = mcp.srcArmature = MocapSourceArmature()
        amt.findArmature(rig)
        amt.correctTPose(rig, scn)
        mcp.sourceArmatures["Automatic"] = amt
        amt.display()
        return amt

        print("Number of misses:")
        for (name, n) in misses.items():
            print("  %14s: %2d" % (name, n))
        print("Best bone map for armature %s:" % best.name)
        amt = mcp.sourceArmatures[best.name]
        for bone in bones:
            try:
                bname,_ = amt.boneNames[canonicalSrcName(bone.name)]
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
    mcp.sourceArmatures = {}
    path = os.path.join(os.path.dirname(__file__), "source_rigs")
    for fname in os.listdir(path):
        file = os.path.join(path, fname)
        (name, ext) = os.path.splitext(fname)
        if ext == ".src" and os.path.isfile(file):
            armature = readSrcArmature(file, name)
            print("ISS", armature)
            mcp.sourceArmatures[armature.name] = armature
    mcp.srcArmatureEnums = [("Automatic", "Automatic", "Automatic")]
    keys = list(mcp.sourceArmatures.keys())
    keys.sort()
    for key in keys:
        mcp.srcArmatureEnums.append((key,key,key))

    bpy.types.Scene.McpSourceRig = EnumProperty(
        items = mcp.srcArmatureEnums,
        name = "Source rig",
        default = 'ACCAD')
    scn.McpSourceRig = 'ACCAD'
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
                amt = armature.boneNames
            elif key == "t-pose:":
                status = 0
                armature.tposeFile = words[1]
                print("T-pose", armature.tposeFile)
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
