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

Python armature
"""

import os
import math
import numpy as np
import transformations as tm
from collections import OrderedDict
import mh2proxy
import exportutils

from .flags import *
from .base_amt import *
from .utils import *

from . import rig_joints
from . import rig_bones

#-------------------------------------------------------------------------------
#   Python Armature
#-------------------------------------------------------------------------------

class PythonArmature(BaseArmature):

    def __init__(self, name, human, config):
        BaseArmature. __init__(self, name, human, config)
        self.headsTails = None
        self.master = None
        self.reparents = {}

        self.useDeformBones = False
        self.useDeformNames = False
        self.useSplitBones = False
        self.splitBones = {}

        self.planes = rig_bones.Planes
        self.planeJoints = []
        self.vertexGroupFiles = []
        self.headName = 'Head'

        self.customShapeFiles = []
        self.loadedShapes = {}


    def distance(self, joint1, joint2):
        vec = self.locations[joint2] - self.locations[joint1]
        return math.sqrt(np.dot(vec,vec))


    def createBones(self, bones):
        """
        config = self.config
        if config.skirtRig == "own":
            self.joints += rig_skirt.Joints
            self.headsTails += rig_skirt.HeadsTails
            self.boneDefs += rig_skirt.Armature

        if config.maleRig:
            self.boneDefs += rig_body.MaleArmature

        if self.config.facepanel:
            self.joints += rig_panel.Joints
            self.headsTails += rig_panel.HeadsTails
            self.boneDefs += rig_panel.Armature

        if False and config.custom:
            (custJoints, custHeadsTails, custArmature, self.customProps) = exportutils.custom.setupCustomRig(config)
            self.joints += custJoints
            self.headsTails += custHeadsTails
            self.boneDefs += custArmature
        """
        self.sortBones(bones)


    def getParent(self, bone):
        return bone.parent
        #return safeGet(self.reparents, bone.name, bone.parent)


    def addIkChains(self, generic, boneInfo, ikChains):
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

                fkBone = boneInfo[fkName] = Bone(self, fkName)
                fkBone.fromInfo((bone, bone.parent, F_WIR, layer<<1))
                ikBone = boneInfo[ikName] = Bone(self, ikName)
                ikBone.fromInfo((bone, bone.parent, F_WIR, layer))

                fkBone.customShape = bone.customShape
                ikBone.customShape = bone.customShape
                bone.customShape = None
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
                    defBone1 = boneInfo[defName1] = Bone(self, defName1)
                    defBone1.fromInfo((bone, defParent, F_DEF+F_CON, L_DEF))
                    defBone2 = boneInfo[defName2] = Bone(self, defName2)
                    defBone2.fromInfo((bone, bone.name, F_DEF, L_DEF))
                elif npieces == 3:
                    self.headsTails[defName1] = (head, ((0.667,head),(0.333,tail)))
                    self.headsTails[defName2] = (((0.667,head),(0.333,tail)), ((0.333,head),(0.667,tail)))
                    self.headsTails[defName3] = (((0.333,head),(0.667,tail)), tail)
                    defBone1 = boneInfo[defName1] = Bone(self, defName1)
                    defBone1.fromInfo((bone, defParent, F_DEF+F_CON, L_DEF))
                    defBone3 = boneInfo[defName3] = Bone(self, defName3)
                    defBone3.fromInfo((bone, bone.name, F_DEF, L_DEF))
                    defBone2 = boneInfo[defName2] = Bone(self, defName2)
                    defBone2.fromInfo((bone, defParent, F_DEF, L_DEF))
                    self.constraints[defName2] = [
                        ('CopyLoc', 0, 1, ["CopyLoc", defName1, (1,1,1), (0,0,0), 1, False]),
                        ('CopyRot', 0, 1, [defName1, defName1, (1,1,1), (0,0,0), False]),
                        ('CopyRot', 0, 0.5, [bone.name, bone.name, (1,1,1), (0,0,0), False])
                    ]

            elif self.useDeformBones:
                defName = "DEF-"+bname
                self.headsTails[defName] = headTail
                defBone = boneInfo[defName] = Bone(self, defName)
                defBone.fromInfo((bone, defParent, F_DEF, L_DEF))
                self.constraints[defName] = [copyTransform(bone.name, bone.name)]

        return boneInfo


    def getVertexGroups(self):

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
                    self.vertexWeights[defName] = vgroup
                else:
                    defName = "DEF-"+bname
                    try:
                        self.bones[defName]
                        self.vertexWeights[defName] = vgroup
                    except KeyError:
                        self.vertexWeights[bname] = vgroup

        elif self.useSplitBones:
            for bname,vgroup in vgroupList:
                base = splitBoneName(bname)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bname, vgroup)
                else:
                    self.vertexWeights[bname] = vgroup

        else:
            for bname,vgroup in vgroupList:
                self.vertexWeights[bname] = vgroup



    def splitVertexGroup(self, bname, vgroup):
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
            self.vertexWeights[defName1] = vgroup1
            self.vertexWeights[defName2] = vgroup2
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
            self.vertexWeights[defName1] = vgroup1
            self.vertexWeights[defName2] = vgroup2
            self.vertexWeights[defName3] = vgroup3


    def getHeadTail(self, bone):
        return self.headsTails[bone]


    def setHeadTail(self, bone, head, tail):
        self.headsTails[bone] = (head,tail)


    def setupToRoll(self):
        if self.config.rigtype not in ["mhx", "basic", "rigify"]:
            print "NOT py", self.config.rigtype
            halt

        self.setupJoints()
        self.setupNormals()
        self.setupPlaneJoints()
        self.moveOriginToFloor()
        self.createBones({})

        for bone in self.bones.values():
            head,tail = self.headsTails[bone.name]
            bone.setBone(self.findLocation(head), self.findLocation(tail))

        for bone in self.bones.values():
            if isinstance(bone.roll, str):
                bone.roll = self.bones[bone.roll].roll
            elif isinstance(bone.roll, Bone):
                bone.roll = bone.roll.roll


    def setup(self):
        self.setupToRoll()
        self.getVertexGroups()


    def setupNormals(self):
        self.normals = {}
        for plane,joints in self.planes.items():
            j1,j2,j3 = joints
            p1 = self.locations[j1]
            p2 = self.locations[j2]
            p3 = self.locations[j3]
            pvec = getUnitVector(p2-p1)
            yvec = getUnitVector(p3-p2)
            if pvec is None or yvec is None:
                self.normals[plane] = None
            else:
                self.normals[plane] = getUnitVector(np.cross(yvec, pvec))


    def setupJoints (self):
        """
        Evaluate symbolic expressions for joint locations and store them in self.locations.
        Joint locations are specified symbolically in the *Joints list in the beginning of the
        rig_*.py files (e.g. ArmJoints in rig_arm.py).
        """

        obj = self.human.meshData
        for (key, typ, data) in self.joints:
            if typ == 'j':
                loc = mh2proxy.calcJointPos(obj, data)
                self.locations[key] = loc
                self.locations[data] = loc
            elif typ == 'v':
                v = int(data)
                self.locations[key] = obj.coord[v]
            elif typ == 'x':
                self.locations[key] = np.array((float(data[0]), float(data[2]), -float(data[1])))
            elif typ == 'vo':
                v = int(data[0])
                offset = np.array((float(data[1]), float(data[3]), -float(data[2])))
                self.locations[key] = (obj.coord[v] + offset)
            elif typ == 'vl':
                ((k1, v1), (k2, v2)) = data
                loc1 = obj.coord[int(v1)]
                loc2 = obj.coord[int(v2)]
                self.locations[key] = (k1*loc1 + k2*loc2)
            elif typ == 'f':
                (raw, head, tail, offs) = data
                rloc = self.locations[raw]
                hloc = self.locations[head]
                tloc = self.locations[tail]
                vec = tloc - hloc
                vraw = rloc - hloc
                x = np.dot(vec, vraw)/np.dot(vec,vec)
                self.locations[key] = hloc + x*vec + np.array(offs)
            elif typ == 'b':
                self.locations[key] = self.locations[data]
            elif typ == 'p':
                x = self.locations[data[0]]
                y = self.locations[data[1]]
                z = self.locations[data[2]]
                self.locations[key] = np.array((x[0],y[1],z[2]))
            elif typ == 'vz':
                v = int(data[0])
                z = obj.coord[v][2]
                loc = self.locations[data[1]]
                self.locations[key] = np.array((loc[0],loc[1],z))
            elif typ == 'X':
                r = self.locations[data[0]]
                (x,y,z) = data[1]
                r1 = np.array([float(x), float(y), float(z)])
                self.locations[key] = np.cross(r, r1)
            elif typ == 'l':
                ((k1, joint1), (k2, joint2)) = data
                self.locations[key] = k1*self.locations[joint1] + k2*self.locations[joint2]
            elif typ == 'o':
                (joint, offsSym) = data
                if type(offsSym) == str:
                    offs = self.locations[offsSym]
                else:
                    offs = np.array(offsSym)
                self.locations[key] = self.locations[joint] + offs
            else:
                raise NameError("Unknown %s" % typ)
        return


    def setupPlaneJoints (self):
        for key,data in self.planeJoints:
            p0,plane,dist = data
            x0 = self.locations[p0]
            p1,p2,p3 = self.planes[plane]
            vec = self.locations[p3] - self.locations[p1]
            vec /= math.sqrt(np.dot(vec,vec))
            n = self.normals[plane]
            t = np.cross(n, vec)
            self.locations[key] = x0 + dist*t


    def moveOriginToFloor(self):
        if self.config.feetOnGround:
            self.origin = self.locations['ground']
            for key in self.locations.keys():
                self.locations[key] = self.locations[key] - self.origin
        else:
            self.origin = np.array([0,0,0], float)
        return


    def findLocation(self, joint):
        if isinstance(joint, str):
            return self.locations[joint]
        else:
            (first, second) = joint
            if isinstance(first, str):
                return self.locations[first] + second
            else:
                w1,j1 = first
                w2,j2 = second
                return w1*self.locations[j1] + w2*self.locations[j2]




