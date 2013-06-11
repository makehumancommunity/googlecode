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
    from .parser import Parser
    if options is None:
        return None
    else:
        log.message("Setup rig %s" % name)
        amt = Armature(name, options)
        amt.parser = Parser(amt, human)
        amt.setup()
        log.message("Using rig with options %s" % options)
        return amt

#-------------------------------------------------------------------------------
#   Armature base class.
#-------------------------------------------------------------------------------

class Armature:

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.parser = None
        self.origin = None
        self.roots = []
        self.bones = OrderedDict()
        self.hierarchy = []

        self.done = False

        self.vertexWeights = OrderedDict([])
        self.isNormalized = False


    def __repr__(self):
        return ("  <BaseArmature %s %s>" % (self.name, self.options.rigtype))


    def setup(self):
        self.parser.setup()
        self.origin = self.parser.origin
        options = self.options

        if options.locale:
            print "Rename %s" % options.locale
            self.rename(options.locale)


    def rescale(self, scale):
        # OK to overwrite bones, because they are not used elsewhere
        for bone in self.bones.values():
            bone.rescale(scale)


    def rename(self, locale):
        locale.load()
        newbones = OrderedDict()
        for bone in self.bones.values():
            bone.rename(locale, newbones)
        self.bones = newbones
        for bname,vgroup in self.vertexWeights.items():
            newname = locale.rename(bname)
            if newname != bname:
                self.vertexWeights[newname] = vgroup
                del self.vertexWeights[bname]


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
                self.roll = computeRoll(self.head, self.tail, normal)


    def rescale(self, scale):
        self.head = scale*self.head
        self.tail = scale*self.tail
        self.length = scale*self.length

        self.matrixRest = None
        self.matrixRelative = None
        self.bindMatrix = None
        self.bindInverse = None


    def rename(self, locale, bones):
        print "REN", self
        self.name = locale.rename(self.name)
        if self.parent:
            self.parent = locale.rename(self.parent)
        for cns in self.constraints:
            print "CNS", cns
        bones[self.name] = self


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




