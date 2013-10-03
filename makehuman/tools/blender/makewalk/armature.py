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

from . import mcp
from .utils import *


class CArmature:

    def __init__(self):
        self.name = "Automatic"
        self.boneNames = OrderedDict()
        self.tposeFile = None


    def display(self, type):
        print("%s Armature: %s" % (type, self.name))
        for bname,mhx in self.boneNames.items():
            print("  %14s %14s" % (bname, mhx))


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
        self.boneNames[canonicalName(pb.name)] = bname


    def findTerminal(self, pb, bnames, prefnames=None):
        if prefnames is None:
            prefnames = bnames
        self.setBone(bnames[0], pb)
        bnames = bnames[1:]
        prefnames = prefnames[1:]
        children = validChildren(pb)
        if bnames:
            if len(children) >= 1:
                child = children[0]
                for pb in children[1:]:
                    if prefnames[0] in pb.name.lower():
                        child = pb
                        break
                return self.findTerminal(child, bnames, prefnames)
            else:
                return None
        else:
            while len(children) == 1:
                pb = children[0]
                children = validChildren(pb)
            return pb


    def findLeg(self, thigh, suffix):
        bnames = ["thigh"+suffix, "shin"+suffix, "foot"+suffix, "toe"+suffix]
        prefnames = ["X", "X", "foot", "toe"]
        shin = validChildren(thigh)[0]
        foot = validChildren(shin)[0]
        if foot and thigh.bone.length < foot.bone.length:
            self.findTerminal(shin, bnames, prefnames)
        else:
            self.findTerminal(thigh, bnames, prefnames)


    def findArm(self, shoulder, suffix):
        bnames = ["deltoid"+suffix, "upper_arm"+suffix, "forearm"+suffix, "hand"+suffix]
        upperarm = validChildren(shoulder)[0]
        forearm = validChildren(upperarm)[0]
        hand = validChildren(forearm)[0]
        if upperarm.bone.length < hand.bone.length:
            bnames = ["shoulder"+suffix] + bnames
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
