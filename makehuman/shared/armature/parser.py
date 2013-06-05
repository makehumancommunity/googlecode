#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Base armature
"""

import os
import math
import gui3d
import mh2proxy
import log
from collections import OrderedDict

import numpy as np
import numpy.linalg as la
import transformations as tm

from .flags import *
from .utils import *
from .armature import Bone

#-------------------------------------------------------------------------------
#   Parser base class.
#-------------------------------------------------------------------------------

class Parser:

    def __init__(self, amt):
        self.armature = amt
        self.locations = {}
        self.origin = [0,0,0]
        self.customShapes = {}
        self.constraints = {}
        self.rotationLimits = {}


    def distance(self, joint1, joint2):
        vec = self.locations[joint2] - self.locations[joint1]
        return math.sqrt(np.dot(vec,vec))


    def prefixWeights(self, weights, prefix):
        pweights = {}
        for name in weights.keys():
            if name in self.heads:
                pweights[name] = weights[name]
            else:
                pweights[prefix+name] = weights[name]
        return pweights


    def createBones(self, boneInfos):
        amt = self.armature
        if amt.options.addConnectingBones:
            extras = []
            for bone in boneInfos.values():
                if bone.parent:
                    head,_ = self.getHeadTail(bone.name)
                    _,ptail = self.getHeadTail(bone.parent)
                    if head != ptail:
                        connector = Bone("_"+bone.name)
                        connector.parent = bone.parent
                        bone.parent = connector
                        extras.append(connector)
                        self.setHeadTail(connector, ptail, head)

            for bone in extras:
                boneInfos[bone.name] = bone

        for bone in boneInfos.values():
            if bone.parent:
                parent = boneInfos[bone.parent]
                parent.children.append(bone)
            elif self.master:
                if bone.name == self.master:
                    amt.roots.append(bone)
                else:
                    bone.parent = self.master
                    master = boneInfos[self.master]
                    master.children.append(bone)
            else:
                amt.roots.append(bone)

        for root in amt.roots:
            self.sortBones(root, amt.hierarchy)

        for bname,data in self.customShapes.items():
            amt.bones[bname].customShape = data

        for bname,data in self.constraints.items():
            try:
                amt.bones[bname].constraints = data
            except KeyError:
                log.message("Warning: constraint for undefined bone %s" % bname)


    def sortBones(self, bone, hier):
        self.armature.bones[bone.name] = bone
        subhier = []
        hier.append([bone, subhier])
        for child in bone.children:
            self.sortBones(child, subhier)


    def addBones(self, dict, boneInfo):
        for bname,info in dict.items():
            bone = boneInfo[bname] = Bone(self.armature, bname)
            bone.fromInfo(info)


    def getParent(self, bone):
        return bone.parent


    def addIkChains(self, generic, boneInfo, ikChains):
        amt = self.armature
        for bname in generic.keys():
            bone = boneInfo[bname]
            headTail = self.headsTails[bname]
            base,ext = splitBoneName(bname)
            bone.parent = self.getParent(bone)

            if base in ikChains.keys():
                value = ikChains[base]
                fkName = base + ".fk" + ext
                ikName = base + ".ik" + ext
                self.headsTails[fkName] = headTail
                self.headsTails[ikName] = headTail

                try:
                    layer,cnsname = value
                    simple = True
                except:
                    count, layer, cnsname, target, pole, lang, rang = value
                    simple = False

                if ext == ".R":
                    layer <<= 16

                fkBone = boneInfo[fkName] = Bone(amt, fkName)
                fkBone.fromInfo((bone, bone.parent, F_WIR, layer<<1))
                ikBone = boneInfo[ikName] = Bone(amt, ikName)
                ikBone.fromInfo((bone, bone.parent, F_WIR, layer))

                customShape = self.customShapes[bone.name]
                self.customShapes[fkName] = customShape
                self.customShapes[ikName] = customShape
                self.customShapes[bone.name] = None
                bone.layers = L_HELP

                self.constraints[bname] = [
                    copyTransform(fkName, cnsname+"FK"),
                    copyTransform(ikName, cnsname+"IK", 0)
                ]

                if not simple:
                    words = bone.parent.rsplit(".", 1)
                    pbase = words[0]
                    if len(words) == 1:
                        pext = ""
                    else:
                        pext = "." + words[1]
                    fkBone.parent = pbase + ".fk" + pext
                    ikBone.parent = pbase + ".ik" + pext

                    ikTarget = target + ".ik" + ext
                    poleTarget = pole + ".ik" + ext
                    if ext == ".L":
                        poleAngle = lang
                    else:
                        poleAngle = rang
                    self.constraints[ikName] = [
                        ('IK', 0, 1, ['IK', ikTarget, count, (poleAngle, poleTarget), (True, False,False)])
                    ]

            else:
                bone.deform = False


    def addDeformBones(self, generic, boneInfo):
        if not (self.useDeformBones or self.useSplitBones):
            return

        amt = self.armature
        for bname in generic.keys():
            bone = boneInfo[bname]
            if not bone.deform:
                continue
            headTail = self.headsTails[bname]
            base,ext = splitBoneName(bname)
            bone.deform = False
            bone.parent = self.getParent(bone)
            if bone.parent and self.useDeformBones:
                pbase, pext = splitBoneName(bone.parent)
                if pbase in self.splitBones.keys():
                    npieces = self.splitBones[pbase][0]
                    defParent = "DEF-" + pbase + ".0" + str(npieces) + pext
                else:
                    parbone = boneInfo[bone.parent]
                    if parbone.deform:
                        defParent = "DEF-" + bone.parent
                    else:
                        defParent = bone.parent
            else:
                defParent = bone.parent

            if self.useSplitBones and (base in self.splitBones.keys()):
                npieces,target,numAfter = self.splitBones[base]
                defName1,defName2,defName3 = splitBonesNames(base, ext, numAfter)
                head,tail = headTail
                fkName = base + ".fk" + ext
                ikName = base + ".ik" + ext
                self.constraints[defName1] = [
                    ('IK', 0, 1, ['IK', target+ext, 1, None, (True, False,True)])
                ]
                if npieces == 2:
                    self.headsTails[defName1] = (head, ((0.5,head),(0.5,tail)))
                    self.headsTails[defName2] = (((0.5,head),(0.5,tail)), tail)
                    defBone1 = boneInfo[defName1] = Bone(amt, defName1)
                    defBone1.fromInfo((bone, defParent, F_DEF+F_CON, L_DEF))
                    defBone2 = boneInfo[defName2] = Bone(amt, defName2)
                    defBone2.fromInfo((bone, bone.name, F_DEF, L_DEF))
                elif npieces == 3:
                    self.headsTails[defName1] = (head, ((0.667,head),(0.333,tail)))
                    self.headsTails[defName2] = (((0.667,head),(0.333,tail)), ((0.333,head),(0.667,tail)))
                    self.headsTails[defName3] = (((0.333,head),(0.667,tail)), tail)
                    defBone1 = boneInfo[defName1] = Bone(amt, defName1)
                    defBone1.fromInfo((bone, defParent, F_DEF+F_CON, L_DEF))
                    defBone3 = boneInfo[defName3] = Bone(amt, defName3)
                    defBone3.fromInfo((bone, bone.name, F_DEF, L_DEF))
                    defBone2 = boneInfo[defName2] = Bone(amt, defName2)
                    defBone2.fromInfo((bone, defParent, F_DEF, L_DEF))
                    self.constraints[defName2] = [
                        ('CopyLoc', 0, 1, ["CopyLoc", defName1, (1,1,1), (0,0,0), 1, False]),
                        ('CopyRot', 0, 1, [defName1, defName1, (1,1,1), (0,0,0), False]),
                        ('CopyRot', 0, 0.5, [bone.name, bone.name, (1,1,1), (0,0,0), False])
                    ]

            elif self.useDeformBones:
                defName = "DEF-"+bname
                self.headsTails[defName] = headTail
                defBone = boneInfo[defName] = Bone(amt, defName)
                defBone.fromInfo((bone, defParent, F_DEF, L_DEF))
                self.constraints[defName] = [copyTransform(bone.name, bone.name)]

        return boneInfo


    def getVertexGroups(self):
        amt = self.armature
        self.vertexGroupFiles += ["leftright"]
        vgroupList = []
        vgroups = {}
        for file in self.vertexGroupFiles:
            filepath = os.path.join("shared/armature/vertexgroups", file+".vgrp")
            readVertexGroups(filepath, vgroups, vgroupList)

        if self.useDeformNames:
            for bname,vgroup in vgroupList:
                base = splitBoneName(bname)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bname, vgroup)
                elif not self.useSplitBones:
                    defName = "DEF-"+bname
                    amt.vertexWeights[defName] = vgroup
                else:
                    defName = "DEF-"+bname
                    try:
                        amt.bones[defName]
                        amt.vertexWeights[defName] = vgroup
                    except KeyError:
                        amt.vertexWeights[bname] = vgroup

        elif self.useSplitBones:
            for bname,vgroup in vgroupList:
                base = splitBoneName(bname)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bname, vgroup)
                else:
                    amt.vertexWeights[bname] = vgroup

        else:
            for bname,vgroup in vgroupList:
                amt.vertexWeights[bname] = vgroup



    def splitVertexGroup(self, bname, vgroup):
        amt = self.armature
        base,ext = splitBoneName(bname)
        npieces,target,numAfter = self.splitBones[base]
        defName1,defName2,defName3 = splitBonesNames(base, ext, numAfter)

        hname,tname = self.headsTails[bname]
        head = self.locations[hname]
        tail = self.locations[tname]
        orig = head + self.origin
        vec0 = tail - head
        vec = vec0/np.dot(vec0,vec0)

        vgroup1 = []
        vgroup2 = []
        vgroup3 = []
        obj = amt.human.meshData
        if npieces == 2:
            for vn,w in vgroup:
                y = obj.coord[vn] - orig
                x = np.dot(vec,y)
                if x < 0:
                    vgroup1.append((vn,w))
                elif x < 0.5:
                    vgroup1.append((vn, (1-x)*w))
                    vgroup2.append((vn, x*w))
                else:
                    vgroup2.append((vn,w))
            amt.vertexWeights[defName1] = vgroup1
            amt.vertexWeights[defName2] = vgroup2
        elif npieces == 3:
            for vn,w in vgroup:
                y = obj.coord[vn] - orig
                x = np.dot(vec,y)
                if x < 0:
                    vgroup1.append((vn,w))
                elif x < 0.5:
                    vgroup1.append((vn, (1-2*x)*w))
                    vgroup2.append((vn, (2*x)*w))
                elif x < 1:
                    vgroup2.append((vn, (2-2*x)*w))
                    vgroup3.append((vn, (2*x-1)*w))
                else:
                    vgroup3.append((vn,w))
            amt.vertexWeights[defName1] = vgroup1
            amt.vertexWeights[defName2] = vgroup2
            amt.vertexWeights[defName3] = vgroup3
