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
Fbx mesh
"""

import math
import numpy as np
import numpy.linalg as la
import transformations as tm

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def countObjects(stuffs, amt):
    char = stuffs[0]
    nMeshes = len(stuffs)
    nVertexGroups = len(char.meshInfo.weights)
    return (nMeshes*nVertexGroups + 1)


def writeObjectDefs(fp, stuffs, amt):
    char = stuffs[0]
    nMeshes = len(stuffs)
    nVertexGroups = len(char.meshInfo.weights)

    fp.write(
'    ObjectType: "Deformer" {\n' +
'    Count: %d' % (nMeshes*nVertexGroups) +
"""
    }

    ObjectType: "Pose" {
        Count: 1
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, stuffs, amt):
    writeBindPose(fp, stuffs, amt)

    for stuff in stuffs:
        name = getStuffName(stuff, amt)
        writeDeformer(fp, name)
        for bone in amt.bones.values():
            try:
                weights = stuff.meshInfo.weights[bone.name]
            except KeyError:
                continue
            writeSubDeformer(fp, name, bone, weights)


def writeDeformer(fp, name):
    id,key = getId("Deformer::%s" % name)

    fp.write(
'    Deformer: ¨%d, "%s", "Skin" {' % (id, key) +
"""
        Version: 101
        Properties70:  {
""" +
'            P: "MHName", "KString", "", "", "%sSkin"' % name +
"""
        }
        Link_DeformAcuracy: 50
    }
""")


def writeSubDeformer(fp, name, bone, weights):
    nVertexWeights = len(weights)
    id,key = getId("SubDeformer::%s_%s" % (bone.name, name))

    fp.write(
'    Deformer: %d, "%s", "Cluster" {\n' % (id, key) +
'        Version: 100\n' +
'        UserData: "", ""\n' +
'        Indexes: *%d {\n' % nVertexWeights +
'            a: ')

    last = nVertexWeights - 1
    for n,data in enumerate(weights):
        vn,w = data
        fp.write(str(vn))
        writeComma(fp, n, last)

    fp.write(
'        } \n' +
'        Weights: *%d {\n' % nVertexWeights +
'            a: ')

    for n,data in enumerate(weights):
        vn,w = data
        fp.write(str(w))
        writeComma(fp, n, last)

    fp.write('        }\n')
    writeMatrix(fp, 'Transform', bone.bindMatrix)
    writeMatrix(fp, 'TransformLink', bone.bindInverse)
    fp.write('    }\n')


def writeBindPose(fp, stuffs, amt):
    id,key = getId("Pose::" + amt.name)
    nBones = len(amt.bones)
    nMeshes = len(stuffs)

    fp.write(
'    Pose: %d, "%s", "BindPose" {\n' % (id, key)+
'        Type: "BindPose"\n' +
'        Version: 100\n' +
'        NbPoseNodes: %d\n' % (1+nMeshes+nBones))

    startLinking()
    amt.calcBindMatrix()
    poseNode(fp, "Model::%s" % amt.name, amt.bindMatrix)

    for stuff in stuffs:
        name = getStuffName(stuff, amt)
        poseNode(fp, "Model::%sMesh" % name, amt.bindMatrix)

    for bone in amt.bones.values():
        bone.calcBindMatrix()
        poseNode(fp, "Model::%s" % bone.name, bone.bindMatrix)

    stopLinking()
    fp.write('    }\n')


def poseNode(fp, key, matrix):
    pid,_ = getId(key)
    matrix[:3,3] = 0
    fp.write(
'        PoseNode:  {\n' +
'            Node: %d\n' % pid)
    writeMatrix(fp, 'Matrix', matrix, "    ")
    fp.write('        }\n')

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, stuffs, amt):

    for stuff in stuffs:
        name = getStuffName(stuff, amt)
        ooLink(fp, 'Deformer::%s' % name, 'Geometry::%s' % name)
        for bone in amt.bones.values():
            subdef = 'SubDeformer::%s_%s' % (bone.name, name)
            try:
                getId(subdef)
            except NameError:
                continue
            ooLink(fp, subdef, 'Deformer::%s' % name)
            ooLink(fp, 'Model::%s' % bone.name, subdef)


