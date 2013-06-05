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

import math
import log
from collections import OrderedDict

import numpy as np
import numpy.linalg as la
import transformations as tm

from .flags import *
from .utils import *

#-------------------------------------------------------------------------------
#   Setup Armature
#-------------------------------------------------------------------------------

def setupArmature(name, human, options):
    amt = Armature(name, human, options)

    if options.rigtype == "basic":
        from .basic import BasicParser
        amt.parser = BasicParser(amt)
        amt.setup()
        log.message("Using basic rig")
        return amt
    elif options.rigtype:
        from .rigfile_amt import RigfileParser
        amt.parser = RigfileParser(amt)
        amt.setup()
        rigfile = "data/rigs/%s.rig" % options.rigtype
        log.message("Using rig file %s" % rigfile)
        return amt
    else:
        return None

#-------------------------------------------------------------------------------
#   Rigging options
#-------------------------------------------------------------------------------

class RigOptions:
    def __init__(self,
            rigtype = "basic",
            scale = 1.0,
            useMuscles = False,
            addConnectingBones = False,
            facepanel = False,
            advancedSpine = False,
            clothesRig = False,
            useMasks = False,
            expressions = False,
        ):

        self.rigtype = rigtype
        self.scale = scale
        self.useSplitBones = False
        self.useMuscles = useMuscles
        self.addConnectingBones = addConnectingBones
        self.feetOnGround = False
        self.facepanel = facepanel
        self.advancedSpine = advancedSpine
        self.clothesRig = clothesRig
        self.useMasks = useMasks
        self.expressions = expressions

#-------------------------------------------------------------------------------
#   Armature base class.
#-------------------------------------------------------------------------------

class Armature:

    def __init__(self, name, human, options):
        self.name = name
        self.human = human
        self.options = options
        self.parser = None
        self.origin = None

        #self.root = None
        self.roots = []
        self.bones = OrderedDict()
        self.hierarchy = []

        self.vertexWeights = OrderedDict([])
        self.isNormalized = False


    def __repr__(self):
        return ("  <BaseArmature %s %s>" % (self.name, self.options.rigtype))


    def setup(self):
        self.parser.setup()
        self.origin = self.parser.origin


    def normalizeVertexWeights(self):
        if self.isNormalized:
            return

        nVerts = len(self.human.meshData.coord)
        wtot = np.zeros(nVerts, float)
        for vgroup in self.vertexWeights.values():
            for vn,w in vgroup:
                wtot[vn] += w

        for bname in self.vertexWeights.keys():
            vgroup = self.vertexWeights[bname]
            weights = np.zeros(len(vgroup), float)
            verts = []
            n = 0
            for vn,w in vgroup:
                verts.append(vn)
                weights[n] = w/wtot[vn]
                n += 1
            self.vertexWeights[bname] = (verts, weights)

        self.isNormalized = True


    def calcBindMatrix(self):
        self.bindMatrix = tm.rotation_matrix(math.pi/2, XUnit)
        self.bindInverse = la.inv(self.bindMatrix)


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
        self.customShape = None
        self.children = []

        self.location = (0,0,0)
        self.group = None
        self.lockLocation = (0,0,0)
        self.lockRotation = (0,0,0)
        self.lockScale = (1,1,1)
        self.ikDof = (1,1,1)
        #self.lock_rotation_w = False
        #self.lock_rotations_4d = False

        self.constraints = []
        self.drivers = []

        # Matrices:
        # matrixRest:       4x4 rest matrix, relative world
        # matrixRelative:   4x4 rest matrix, relative parent
        # matrixPose:       4x4 pose matrix, relative parent and own rest pose
        # matrixGlobal:     4x4 matrix, relative world
        # matrixVerts:      4x4 matrix, relative world and own rest pose

        self.matrixRest = None
        self.matrixRelative = None
        self.bindMatrix = None
        self.bindInverse = None


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
                normal = m2b(self.armature.parser.normals[self.roll])
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


    def getBindMatrixCollada(self):
        self.calcRestMatrix()
        rotX = tm.rotation_matrix(math.pi/2, XUnit)
        mat4 = np.dot(rotX, self.matrixRest)
        return la.inv(mat4)


    def calcBindMatrix(self):
        if self.bindMatrix is not None:
            return
        self.calcRestMatrix()
        self.bindInverse = np.transpose(self.matrixRest)
        self.bindMatrix = la.inv(self.bindInverse)





