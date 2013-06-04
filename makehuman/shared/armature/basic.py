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

Basic armature
"""

from .flags import *
from .python_amt import *

from . import rig_joints
from . import rig_bones
from . import rig_muscle
from . import rig_face


class BasicArmature(PythonArmature):

    def __init__(self, name, human, options):
        PythonArmature. __init__(self, name, human, options)
        self.options.rigtype = "basic"
        self.root = "hips"

        if options.useMuscles:
            self.vertexGroupFiles = ["head", "muscles", "hand"]
        else:
            self.vertexGroupFiles = ["head", "bones", "hand"]
        self.headName = 'head'
        self.useDeformBones = False
        self.useDeformNames = False
        if options.useSplitBones:
            self.useSplitBones = True
            self.splitBones = {
                "forearm" :     (3, "hand", False),
            }

        self.joints = (
            rig_joints.Joints +
            rig_bones.Joints +
            rig_face.Joints
        )
        if options.useMuscles:
            self.joints += rig_muscle.Joints

        self.headsTails = mergeDicts([
            rig_bones.HeadsTails,
            rig_face.HeadsTails
        ])
        if options.useMuscles:
            addDict(rig_muscle.HeadsTails, self.headsTails)

        self.constraints = mergeDicts([
            rig_bones.Constraints,
            rig_face.Constraints
        ])
        if options.useMuscles:
            addDict(rig_muscle.Constraints, self.constraints)

        self.rotationLimits = mergeDicts([
            rig_bones.RotationLimits,
            rig_face.RotationLimits
        ])
        if options.useMuscles:
            addDict(rig_muscle.RotationLimits, self.rotationLimits)

        self.customShapes = mergeDicts([
            rig_bones.CustomShapes,
            rig_face.CustomShapes
        ])
        if options.useMuscles:
            addDict(rig_muscle.CustomShapes, self.customShapes)

        self.objectProps = rig_bones.ObjectProps
        self.armatureProps = rig_bones.ArmatureProps


    def createBones(self, boneInfo):
        self.addBones(rig_bones.Armature, boneInfo)
        self.addDeformBones(rig_bones.Armature, boneInfo)
        if self.options.useMuscles:
            self.addBones(rig_muscle.Armature, boneInfo)
        self.addBones(rig_face.Armature, boneInfo)
        PythonArmature.createBones(self, boneInfo)

