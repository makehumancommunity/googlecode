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

from .flags import *
from .mhx_armature import *

from . import rig_joints
from . import rig_bones
from . import rig_muscle
from . import rig_face


class RigifyArmature(ExportArmature):

    def __init__(self, name, human, config):   
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = 'rigify'
        self.vertexGroupFiles = ["head", "basic"]
        self.master = None
        self.gizmos = None
        self.boneLayers = "08a80caa"
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
                

    def createBones(self, bones):
        addBones(rig_bones.Armature, bones)
        addBones(rig_muscle.Armature, bones)
        addBones(rig_face.Armature, bones)
        ExportArmature.createBones(self, bones)


    def setupCustomShapes(self, fp):
        return        
