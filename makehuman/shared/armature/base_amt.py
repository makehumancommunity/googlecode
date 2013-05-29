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

#-------------------------------------------------------------------------------        
#   Armature base class.
#-------------------------------------------------------------------------------        
       
class BaseArmature:

    def __init__(self, name, human, config):
        self.name = name
        self.human = human
        self.mesh = human.meshData
        self.boneLayers = "00000001"
        self.config = config
        self.rigtype = config.rigtype
        self.addConnectingBones = config.addConnectingBones
        self.root = None
        self.master = None
        self.proxies = {}
        self.roots = []
        self.bones = OrderedDict()
        self.hierarchy = []

        self.locations = {}
        self.origin = [0,0,0]
        self.loadedShapes = {}
        self.constraints = {}
        self.rotationLimits = {}
        
        self.vertexWeights = OrderedDict([])
                

    def __repr__(self):
        return ("  <BaseArmature %s %s>" % (self.name, self.rigtype))
        

    def prefixWeights(self, weights, prefix):
        pweights = {}
        for name in weights.keys():
            if name in self.heads:
                pweights[name] = weights[name]
            else:
                pweights[prefix+name] = weights[name]
        return pweights


    def sortBones(self, boneInfos):
        if self.addConnectingBones:            
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
                    self.roots.append(bone)
                else:
                    bone.parent = self.master
                    master = boneInfos[self.master]
                    master.children.append(bone)
            else:
                self.roots.append(bone)

        for root in self.roots:            
            self.sortBones1(root, self.hierarchy)


    def sortBones1(self, bone, hier):
        self.bones[bone.name] = bone
        subhier = []
        hier.append([bone, subhier])
        for child in bone.children:
            self.sortBones1(child, subhier)
            
    
    def addBones(self, dict, boneInfo):
        for bname,info in dict.items():
            bone = boneInfo[bname] = Bone(self, bname)
            bone.fromInfo(info)
        

class Bone:
    def __init__(self, amt, name):
        self.name = name
        self.armature = amt
        self.head = None
        self.tail = None
        self.roll = 0
        self.parent = None
        self.flags = 0
        self.layers = L_MAIN        
        self.length = 0
        self.children = []        
    
        self.location = (0,0,0)
        self.lock_location = (False,False,False)
        self.lock_rotation = (False,False,False)
        self.lock_rotation_w = False
        self.lock_rotations_4d = False
        self.lock_scale = (False,False,False)
        
        self.constraints = []
        self.drivers = []
        self.rotationLimits = []

        # Matrices:
        # matrixRest:       4x4 rest matrix, relative world
        # matrixRelative:   4x4 rest matrix, relative parent 
        # matrixPose:       4x4 pose matrix, relative parent and own rest pose
        # matrixGlobal:     4x4 matrix, relative world
        # matrixVerts:      4x4 matrix, relative world and own rest pose
        
        self.matrixRest = None
        self.matrixRelative = None
        self.matrixBind = None
    
        self.matrixPose = None
        self.matrixGlobal = None
        self.matrixVerts = None


    def __repr__(self):
        return "<Bone %s>" % self.name
        
        
    def fromInfo(self, info):        
        self.roll, self.parent, flags, self.layers = info
        self.setFlags(flags)
        if self.roll == None:
            halt


    def setFlags(self, flags):
        self.flags = flags
        self.conn = (flags & F_CON != 0)
        self.deform = (flags & F_DEF != 0)
        self.restr = (flags & F_RES != 0)
        self.wire = (flags & F_WIR != 0)
        self.lloc = (flags & F_NOLOC == 0)
        self.lock = (flags & F_LOCK != 0)
        self.cyc = (flags & F_NOCYC == 0)
        self.hide = (flags & F_HID)
        self.norot = (flags & F_NOROT)
        self.scale = (flags & F_SCALE)


    def setBone(self, head, tail):
        self.head = head
        self.tail = tail
        vec = tail - head
        self.length = math.sqrt(np.dot(vec,vec))
        
        if isinstance(self.roll, str):
            if self.roll[0:5] == "Plane":
                normal = m2b(self.armature.normals[self.roll])
                self.computeRoll(normal)


    def computeRoll(self, normal):
        if normal is None:
            return

        p1 = m2b(self.head)
        p2 = m2b(self.tail)
        xvec = normal
        yvec = getUnitVector(p2-p1)
        xy = np.dot(xvec,yvec)
        yvec = getUnitVector(yvec-xy*xvec)
        zvec = getUnitVector(np.cross(xvec, yvec))
        if zvec is None:
            return 0
        else:
            mat = np.array((xvec,yvec,zvec))
            
        checkOrthogonal(mat)
        quat = tm.quaternion_from_matrix(mat)
        if abs(quat[0]) < 1e-4:
            self.roll = 0
        else:
            self.roll = math.pi - 2*math.atan(quat[2]/quat[0])
        if self.roll > math.pi:
            self.roll -= 2*math.pi
                

    def calcRestMatrix(self): 
        if self.matrixRest is not None:
            return 

        _,self.matrixRest = getMatrix(self.head, self.tail, self.roll)
                
        if self.parent:
            parbone = self.armature.bones[self.parent]
            self.matrixRelative = np.dot(la.inv(parbone.matrixRest), self.matrixRest)
        else:
            self.matrixRelative = self.matrixRest
        
        rotX = tm.rotation_matrix(math.pi/2, XUnit)
        mat4 = np.dot(rotX, self.matrixRest)
        mat3 = np.transpose(mat4[:3,:3])
        self.matrixBind = np.identity(4, float)
        self.matrixBind[:3,:3] = mat3
        self.matrixBind[:3,3] = -np.dot(mat3, mat4[:3,3])

        return        
        print self.name, self.roll, self.length
        print(self.matrixRest)        
        print(self.matrixRelative)
        print(self.matrixBind)
        



        