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
from .utils import *
from .parser import Parser
from .armature import *

from . import rig_joints
from . import rig_bones

#-------------------------------------------------------------------------------
#   Python Parser
#-------------------------------------------------------------------------------

class PythonParser(Parser):

    def __init__(self, amt):
        Parser. __init__(self, amt)
        self.headsTails = None
        self.master = None
        self.reparents = {}

        self.useDeformBones = False
        self.useDeformNames = False
        self.useSplitBones = False
        self.splitBones = {}

        self.normals = {}
        self.planes = rig_bones.Planes
        self.planeJoints = []
        self.vertexGroupFiles = []
        self.headName = 'Head'

        self.customTargetFiles = []
        self.loadedShapes = {}


    def createBones(self, boneInfos):
        """
        options = self.options
        if options.skirtRig == "own":
            self.joints += rig_skirt.Joints
            self.headsTails += rig_skirt.HeadsTails
            self.boneDefs += rig_skirt.Armature

        if options.maleRig:
            self.boneDefs += rig_body.MaleArmature

        if self.options.facepanel:
            self.joints += rig_panel.Joints
            self.headsTails += rig_panel.HeadsTails
            self.boneDefs += rig_panel.Armature

        if False and options.custom:
            (custJoints, custHeadsTails, custArmature, self.customProps) = exportutils.custom.setupCustomRig(options)
            self.joints += custJoints
            self.headsTails += custHeadsTails
            self.boneDefs += custArmature
        """
        Parser.createBones(self, boneInfos)


    def getHeadTail(self, bone):
        return self.headsTails[bone]


    def setHeadTail(self, bone, head, tail):
        self.headsTails[bone] = (head,tail)


    def setup(self):
        self.setupToRoll()
        self.getVertexGroups()


    def setupToRoll(self):
        amt = self.armature
        self.setupJoints(amt.human)
        self.setupNormals()
        self.setupPlaneJoints()
        self.moveOriginToFloor(amt.options.feetOnGround)
        self.createBones({})

        for bone in amt.bones.values():
            head,tail = self.headsTails[bone.name]
            bone.setBone(self.findLocation(head), self.findLocation(tail))

        for bone in amt.bones.values():
            if isinstance(bone.roll, str):
                bone.roll = amt.bones[bone.roll].roll
            elif isinstance(bone.roll, Bone):
                bone.roll = bone.roll.roll


    def setupNormals(self):
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


    def setupJoints (self, human):
        """
        Evaluate symbolic expressions for joint locations and store them in self.locations.
        Joint locations are specified symbolically in the *Joints list in the beginning of the
        rig_*.py files (e.g. ArmJoints in rig_arm.py).
        """

        obj = human.meshData
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


    def moveOriginToFloor(self, feetOnGround):
        if feetOnGround:
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




