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
from .mhx_armature import *

from . import rig_joints
from . import rig_bones
from . import rig_muscle
from . import rig_face
from . import rig_mhx


class BasicArmature(ExportArmature):

    def __init__(self, name, human, config):   
        import gizmos_general
        
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = "basic"
        self.boneLayers = "08a80caa"

        self.vertexGroupFiles = ["head", "basic"]
        self.gizmos = gizmos_general.asString()
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
        ExportArmature.createBones(self, bones)
            

    def writeDrivers(self, fp):
        rig_face.DeformDrivers(fp, self)        
        mhx_drivers.writePropDrivers(fp, self, rig_face.PropDrivers, "", "Mha")
        mhx_drivers.writePropDrivers(fp, self, rig_face.SoftPropDrivers, "", "Mha")
        return []

