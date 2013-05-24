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
from .python import *

from . import rig_joints
from . import rig_bones
from . import rig_muscle
from . import rig_face


class BasicArmature(PythonArmature):

    def __init__(self, name, human, config):   
        PythonArmature. __init__(self, name, human, config)
        self.rigtype = "basic"
        self.boneLayers = "08a80caa"

        self.vertexGroupFiles = [
            PythonVertexGroupDirectory + "head", 
            PythonVertexGroupDirectory + "basic"
        ]
        self.headName = 'head'
        self.useDeformBones = False
        self.useDeformNames = False
        self.useSplitBones = True
        self.splitBones = {
            "forearm" :     (3, "hand", False),
        }

        self.joints = (
            rig_joints.Joints +
            rig_bones.Joints +
            rig_muscle.Joints +
            rig_face.Joints
        )
        
        self.headsTails = mergeDicts([
            rig_bones.HeadsTails,
            rig_muscle.HeadsTails,
            rig_face.HeadsTails
        ])

        self.constraints = mergeDicts([
            rig_bones.Constraints,
            rig_muscle.Constraints,
            rig_face.Constraints
        ])

        self.rotationLimits = mergeDicts([
            rig_bones.RotationLimits,
            rig_muscle.RotationLimits,
            rig_face.RotationLimits
        ])

        self.customShapes = mergeDicts([
            rig_bones.CustomShapes,
            rig_muscle.CustomShapes,
            rig_face.CustomShapes
        ])

        self.objectProps = rig_bones.ObjectProps
        self.armatureProps = rig_bones.ArmatureProps
        
    
    def createBones(self, bones):
        addBones(rig_bones.Armature, bones)
        self.addDeformBones(rig_bones.Armature, bones),
        addBones(rig_muscle.Armature, bones)
        addBones(rig_face.Armature, bones)
        PythonArmature.createBones(self, bones)
            


