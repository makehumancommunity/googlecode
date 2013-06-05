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

MHX armature
"""

import armature
from armature.python_amt import PythonParser
from .mhx_armature import ExportArmature

from armature import rig_joints
from armature import rig_bones
from armature import rig_muscle
from armature import rig_face
from . import rig_rigify

from armature.flags import *
from armature.utils import *


class RigifyArmature(ExportArmature):

    def __init__(self, name, human, options):
        ExportArmature.__init__(self, name, human, options)
        self.parser = RigifyParser(self)
        self.visibleLayers = "08a80caa"


class RigifyParser(PythonParser):

    def __init__(self, amt):
        PythonParser.__init__(self, amt)
        if amt.options.useMuscles:
            self.vertexGroupFiles = ["head", "muscles", "hand"]
        else:
            self.vertexGroupFiles = ["head", "bones", "hand"]
        self.master = None
        self.gizmos = None
        self.headName = 'head'

        self.useDeformBones = False
        self.useDeformNames = True
        self.useSplitBones = False
        self.splitBones = {
            "upper_arm" :   (2, "forearm", False),
            "forearm" :     (2, "hand", False),
            "thigh" :       (2, "shin", False),
            "shin" :        (2, "foot", False),

            "thumb.01" :    (2, "thumb.02", True),
            "f_index.01" :  (2, "f_index.02", True),
            "f_middle.01" : (2, "f_middle.02", True),
            "f_ring.01" :   (2, "f_ring.02", True),
            "f_pinky.01" :  (2, "f_pinky.02", True),
        }

        self.joints = (
            rig_joints.Joints +
            rig_bones.Joints +
            rig_rigify.Joints +
            rig_muscle.Joints +
            rig_face.Joints
        )

        self.headsTails = mergeDicts([
            rig_bones.HeadsTails,
            rig_rigify.HeadsTails,
            rig_muscle.HeadsTails,
            rig_face.HeadsTails
        ])

        self.constraints = mergeDicts([
            rig_bones.Constraints,
            rig_muscle.Constraints,
            rig_face.Constraints
        ])

        self.objectProps = (
            rig_bones.ObjectProps +
            [("MhxRig", '"Rigify"'),
             ("MhxRigify", True)]
        )
        self.armatureProps = rig_bones.ArmatureProps

        self.boneGroups = []
        self.rotationLimits = {}
        self.customShapes = {}
        self.constraints = {}


    def createBones(self, boneInfo):
        self.addBones(rig_bones.Armature, boneInfo)
        self.addBones(rig_muscle.Armature, boneInfo)
        self.addBones(rig_face.Armature, boneInfo)
        PythonParser.createBones(self, boneInfo)


    def setupCustomShapes(self, fp):
        return
