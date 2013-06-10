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
import log
from collections import OrderedDict

import numpy as np
import numpy.linalg as la
import transformations as tm

from .flags import *
from .utils import *
from .armature import Bone

from . import rig_merge

#-------------------------------------------------------------------------------
#   Parser base class.
#-------------------------------------------------------------------------------

class Parser:

    def __init__(self, amt, human):
        self.armature = amt
        self.human = human
        self.locations = {}
        self.origin = [0,0,0]
        self.customShapes = {}
        self.constraints = {}
        self.rotationLimits = {}

        self.drivers = []
        self.lrDrivers = []


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


    def createBones(self, boneInfo):
        amt = self.armature
        options = amt.options

        self.getVertexGroups()

        if options.mergeSpine:
            self.mergeBones(rig_merge.SpineMergers, boneInfo)

        if options.mergeFingers:
            self.mergeBones(rig_merge.FingerMergers, boneInfo)

        if options.mergePalms:
            self.mergeBones(rig_merge.PalmMergers, boneInfo)

        if options.mergeHead:
            self.mergeBones(rig_merge.HeadMergers, boneInfo)

        for bone in boneInfo.values():
            if bone.parent:
                parent = boneInfo[bone.parent]
                parent.children.append(bone)
            elif self.master:
                if bone.name == self.master:
                    amt.roots.append(bone)
                else:
                    bone.parent = self.master
                    master = boneInfo[self.master]
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
        """
        Adds FK and IK versions of the bones in the chain, and add CopyTransform
        constraints to the original bone, which is moved to the L_HELP layer. E.g.
        shin.L => shin.fk.L, shin.ik.L, shin.L
        """

        amt = self.armature
        options = amt.options

        for bname in generic.keys():
            bone = boneInfo[bname]
            headTail = self.headsTails[bname]
            base,ext = splitBoneName(bname)
            bone.parent = self.getParent(bone)

            if base in ikChains.keys():
                print bone, bone.parent
                pbase,pext = splitBoneName(bone.parent)
                value = ikChains[base]
                type = value[0]
                if type == "DownStream":
                    _,layer,cnsname = value
                    fkParent = getFkName(pbase,pext)
                elif type == "Upstream":
                    _,layer,cnsname = value
                    fkParent = ikParent = bone.parent
                elif type == "Leaf":
                    _, layer, count, cnsname, target, pole, lang, rang = value
                    fkParent = getFkName(pbase,pext)
                    ikParent = getIkName(pbase,pext)
                else:
                    raise NameError("Unknown IKChain type %s" % type)

                if ext == ".R":
                    layer <<= 16

                fkName = getFkName(base,ext)
                self.headsTails[fkName] = headTail
                fkBone = boneInfo[fkName] = Bone(amt, fkName)
                fkBone.fromInfo((bname, fkParent, F_WIR, layer<<1))

                customShape = self.customShapes[bone.name]
                self.customShapes[fkName] = customShape
                self.customShapes[bone.name] = None
                bone.layers = L_HELP

                cns = copyTransform(fkName, cnsname+"FK")
                try:
                    self.constraints[bname].append(cns)
                except KeyError:
                    self.constraints[bname] = [cns]

                if type == "DownStream":
                    continue

                ikName = base + ".ik" + ext
                self.headsTails[ikName] = headTail
                ikBone = boneInfo[ikName] = Bone(amt, ikName)
                ikBone.fromInfo((bname, ikParent, F_WIR, layer))

                self.customShapes[ikName] = customShape
                self.constraints[bname].append( copyTransform(ikName, cnsname+"IK", 0) )

                if type == "Leaf":
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
        """
        Add deform bones with CopyTransform constraints to the original bone.
        Deform bones start with "DEF-", as in Rigify.
        Also split selected bones into two or three parts for better deformation,
        and constrain them to copy the partially.
        E.g. forearm.L => DEF-forearm.01.L, DEF-forearm.02.L, DEF-forearm.03.L
        """

        amt = self.armature
        options = amt.options

        if not (options.useDeformBones or options.useSplitBones):
            return

        for bname in generic.keys():
            bone = boneInfo[bname]
            if not bone.deform:
                continue
            headTail = self.headsTails[bname]
            base,ext = splitBoneName(bname)
            bone.deform = False
            bone.parent = self.getParent(bone)
            if bone.parent and options.useDeformBones:
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

            if options.useSplitBones and (base in self.splitBones.keys()):
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

            elif options.useDeformBones:
                defName = "DEF-"+bname
                self.headsTails[defName] = headTail
                defBone = boneInfo[defName] = Bone(amt, defName)
                defBone.fromInfo((bone, defParent, F_DEF, L_DEF))
                self.constraints[defName] = [copyTransform(bone.name, bone.name)]

        return boneInfo


    def getVertexGroups(self):
        """
        Read vertex groups from specified files, and do some manipulations.
        If the rig has deform bones, prefix vertex group names with "DEF-".
        If some bones are split, split the vertex groups into two or three.
        Rigify uses deform and split names but not bones, because the rigify
        script will fix that in Blender.
        """

        amt = self.armature
        options = amt.options

        self.vertexGroupFiles += ["leftright"]
        vgroupList = []
        vgroups = {}
        for file in self.vertexGroupFiles:
            filepath = os.path.join("shared/armature/vertexgroups", file+".vgrp")
            readVertexGroups(filepath, vgroups, vgroupList)

        if options.useDeformNames:
            for bname,vgroup in vgroupList:
                base = splitBoneName(bname)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bname, vgroup)
                elif not options.useSplitBones:
                    defName = "DEF-"+bname
                    amt.vertexWeights[defName] = vgroup
                else:
                    defName = "DEF-"+bname
                    try:
                        amt.bones[defName]
                        amt.vertexWeights[defName] = vgroup
                    except KeyError:
                        amt.vertexWeights[bname] = vgroup

        elif options.useSplitBones:
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
        """
        Splits a vertex group into two or three, with weights distributed
        linearly along the bone.
        """

        amt = self.armature
        base,ext = splitBoneName(bname)
        npieces,target,numAfter = self.splitBones[base]
        defName1,defName2,defName3 = splitBonesNames(base, ext, numAfter)

        head,tail = self.headsTails[bname]
        vec = getUnitVector(self.locations[head] - self.locations[tail])
        orig = self.locations[head] + self.origin

        vgroup1 = []
        vgroup2 = []
        vgroup3 = []
        obj = self.human.meshData
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


    def mergeBones(self, mergers, boneInfo):
        amt = self.armature
        for bname, merged in mergers.items():
            vgroup = amt.vertexWeights[bname]
            for mbone in merged:
                if mbone != bname:
                    vgroup += amt.vertexWeights[mbone]
                    del amt.vertexWeights[mbone]
                    del boneInfo[mbone]
                    for child in boneInfo.values():
                        if child.parent == mbone:
                            child.parent = bname
        amt.vertexWeights[bname] = mergeWeights(vgroup)


    def addCSysBones(self, csysList, boneInfo):
        """
        Add a local coordinate system consisting of six bones around the head
        of a given bone. Useful for setting up ROTATION_DIFF drivers for
        corrective shapekeys.
        Y axis: parallel to bone.
        X axis: main bend axis, normal to plane.
        Z axis: third axis.
        """

        for bname,ikTarget in csysList:
            bone = boneInfo[bname]
            parent = self.getParent(bone)
            head,_ = self.headsTails[bname]

            self.addCSysBone(bname, "_X1", boneInfo, parent, head, (1,0,0), 0)
            self.addCSysBone(bname, "_X2", boneInfo, parent, head, (-1,0,0), 0)
            csysY1 = self.addCSysBone(bname, "_Y1", boneInfo, parent, head, (0,1,0), 90*D)
            csysY2 = self.addCSysBone(bname, "_Y2", boneInfo, parent, head, (0,-1,0), -90*D)
            self.addCSysBone(bname, "_Z1", boneInfo, parent, head, (0,0,1), 0)
            self.addCSysBone(bname, "_Z2", boneInfo, parent, head, (0,0,-1), 0)

            self.constraints[csysY1] = [('IK', 0, 1, ['IK', ikTarget, 1, None, (True, False,False)])]
            self.constraints[csysY2] = [('IK', 0, 1, ['IK', ikTarget, 1, None, (True, False,False)])]


    def addCSysBone(self, bname, infix, boneInfo, parent, head, offs, roll):
        csys = csysBoneName(bname, infix)
        bone = boneInfo[csys] = Bone(self.armature, csys)
        bone.fromInfo((roll, parent, 0, L_HELP2))
        self.headsTails[csys] = (head, (head,offs))
        return csys


    def fixCSysBones(self, csysList):
        """
        Rotate the coordinate system bones into place.
        """

        amt = self.armature
        for bone in amt.bones.values():
            bone.calcRestMatrix()

        for bname,ikTarget in csysList:
            bone = amt.bones[bname]
            mat = bone.matrixRest

            self.fixCSysBone(bname, "_X1", mat, 0, (1,0,0), 90*D)
            self.fixCSysBone(bname, "_X2", mat, 0, (1,0,0), -90*D)
            self.fixCSysBone(bname, "_Y1", mat, 1, (0,1,0), 90*D)
            self.fixCSysBone(bname, "_Y2", mat, 1, (0,1,0), -90*D)
            self.fixCSysBone(bname, "_Z1", mat, 2, (0,0,1), 90*D)
            self.fixCSysBone(bname, "_Z2", mat, 2, (0,0,1), -90*D)


    def fixCSysBone(self, bname, infix, mat, index, axis, angle):
        csys = csysBoneName(bname, infix)
        bone = self.armature.bones[csys]
        rot = tm.rotation_matrix(angle, axis)
        cmat = np.dot(mat, rot)
        bone.tail = bone.head + self.armature.bones[bname].length * cmat[:3,1]
        normal = getUnitVector(mat[:3,index])
        bone.roll = computeRoll(bone.head, bone.tail, normal)


