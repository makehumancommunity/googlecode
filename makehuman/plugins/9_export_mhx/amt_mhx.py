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
from . import mhx_armature
from .mhx_armature import ExportArmature

from armature import rig_joints
from armature import rig_bones
from armature import rig_muscle
from armature import rig_face
from . import rig_master
from . import rig_mhx

from . import mhx_drivers

from armature.flags import *
from armature.utils import *

class MhxArmature(ExportArmature):

    def __init__(self, name, human, options):
        ExportArmature.__init__(self, name, human, options)
        self.parser = MhxParser(self)
        self.visibleLayers = "0068056b"


    def setupCustomShapes(self, fp):
        mhx_armature.writeCustomEmpty(fp)
        fp.write(self.parser.gizmos)
        mhx_armature.setupSimpleCustomTargets(fp)
        if self.options.facepanel:
            import gizmos_panel
            setupCube(fp, "MHCube025", 0.25, 0)
            setupCube(fp, "MHCube05", 0.5, 0)
            gizmos = gizmos_panel.asString()
            fp.write(gizmos)


    def writeControlPoses(self, fp, options):
        self.writeBoneGroups(fp)
        ExportArmature.writeControlPoses(self, fp, options)


    def writeDrivers(self, fp):
        driverList = (
            #mhx_drivers.writePropDrivers(fp, self, rig_mhx.PropDrivers, "", "Mha") +
            mhx_drivers.writePropDrivers(fp, self, rig_mhx.PropLRDrivers, "L", "Mha") +
            mhx_drivers.writePropDrivers(fp, self, rig_mhx.PropLRDrivers, "R", "Mha") +
            mhx_drivers.writeDrivers(fp, True, rig_face.DeformDrivers(fp, self))
        )
        return driverList

        if options.advancedSpine:
            driverList += mhx_drivers.writePropDrivers(fp, self, rig_body.PropDriversAdvanced, "", "Mha")
        fingDrivers = rig_finger.getPropDrivers()
        driverList += (
            mhx_drivers.writePropDrivers(fp, self, fingDrivers, "_L", "Mha") +
            mhx_drivers.writePropDrivers(fp, self, fingDrivers, "_R", "Mha")
        )
        return driverList


    def writeActions(self, fp):
        #rig_arm.WriteActions(fp)
        #rig_leg.WriteActions(fp)
        #rig_finger.WriteActions(fp)
        return


    def writeProperties(self, fp):
        ExportArmature.writeProperties(self, fp)

        fp.write("""
  Property MhaArmIk_L 0.0 Left_arm_FK/IK ;
  PropKeys MhaArmIk_L "min":0.0,"max":1.0, ;

  Property MhaArmHinge_L False Left_arm_hinge ;
  PropKeys MhaArmHinge_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaElbowPlant_L False Left_elbow_plant ;
  PropKeys MhaElbowPlant_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaHandFollowsWrist_L True Left_hand_follows_wrist ;
  PropKeys MhaHandFollowsWrist_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegIk_L 0.0 Left_leg_FK/IK ;
  PropKeys MhaLegIk_L "min":0.0,"max":1.0, ;

  Property MhaLegIkToAnkle_L False Left_leg_IK_to_ankle ;
  PropKeys MhaLegIkToAnkle_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsFoot_L True Left_knee_follows_foot ;
  # PropKeys MhaKneeFollowsFoot_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsHip_L False Left_knee_follows_hip ;
  # PropKeys MhaKneeFollowsHip_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaElbowFollowsWrist_L False Left_elbow_follows_wrist ;
  # PropKeys MhaElbowFollowsWrist_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaElbowFollowsShoulder_L True Left_elbow_follows_shoulder ;
  # PropKeys MhaElbowFollowsShoulder_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaFingerControl_L True Left_fingers_controlled ;
  PropKeys MhaFingerControl_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaArmIk_R 0.0 Right_arm_FK/IK ;
  PropKeys MhaArmIk_R "min":0.0,"max":1.0, ;

  Property MhaArmHinge_R False Right_arm_hinge ;
  PropKeys MhaArmHinge_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaElbowPlant_R False Right_elbow_plant ;
  PropKeys MhaElbowPlant_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegIk_R 0.0 Right_leg_FK/IK ;
  PropKeys MhaLegIk_R "min":0.0,"max":1.0, ;

  Property MhaHandFollowsWrist_R True Right_hand_follows_wrist ;
  PropKeys MhaHandFollowsWrist_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegIkToAnkle_R False Right_leg_IK_to_ankle ;
  PropKeys MhaLegIkToAnkle_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsFoot_R True Right_knee_follows_foot ;
  # PropKeys MhaKneeFollowsFoot_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsHip_R False Right_knee_follows_hip ;
  # PropKeys MhaKneeFollowsHip_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaElbowFollowsWrist_R False Right_elbow_follows_wrist ;
  # PropKeys MhaElbowFollowsWrist_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaElbowFollowsShoulder_R True Right_elbow_follows_shoulder ;
  # PropKeys MhaElbowFollowsShoulder_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaGazeFollowsHead 1.0 Gaze_follows_world_or_head ;
  PropKeys MhaGazeFollowsHead "type":'BOOLEAN',"min":0.0,"max":1.0, ;

  Property MhaFingerControl_R True Right_fingers_controlled ;
  PropKeys MhaFingerControl_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaArmStretch_L 0.1 Left_arm_stretch_amount ;
  PropKeys MhaArmStretch_L "min":0.0,"max":1.0, ;

  Property MhaLegStretch_L 0.1 Left_leg_stretch_amount ;
  PropKeys MhaLegStretch_L "min":0.0,"max":1.0, ;

  Property MhaArmStretch_R 0.1 Right_arm_stretch_amount ;
  PropKeys MhaArmStretch_R "min":0.0,"max":1.0, ;

  Property MhaLegStretch_R 0.1 Right_leg_stretch_amount ;
  PropKeys MhaLegStretch_R "min":0.0,"max":1.0, ;

  Property MhaRotationLimits 0.8 Influence_of_rotation_limit_constraints ;
  PropKeys MhaRotationLimits "min":0.0,"max":1.0, ;

  Property MhaFreePubis 0.5 Pubis_moves_freely ;
  PropKeys MhaFreePubis "min":0.0,"max":1.0, ;

  Property MhaBreathe 0.0 Breathe ;
  PropKeys MhaBreathe "min":-0.5,"max":2.0, ;
""")

        if self.options.advancedSpine:

            fp.write("""
  Property MhaSpineInvert False Spine_from_shoulders_to_pelvis ;
  PropKeys MhaSpineInvert "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaSpineIk False Spine_FK/IK ;
  PropKeys MhaSpineIk "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaSpineStretch 0.2 Spine_stretch_amount ;
  PropKeys MhaSpineStretch "min":0.0,"max":1.0, ;
""")


class MhxParser(PythonParser):

    def __init__(self, amt):
        import gizmos_mhx, gizmos_general

        PythonParser.__init__(self, amt)
        self.useDeformBones = True
        self.useDeformNames = True
        self.useSplitBones = True
        self.splitBones = {
            "forearm" :     (3, "hand", False),
        }
        self.planeJoints = rig_mhx.PlaneJoints

        self.boneGroups = [
            ('Master', 'THEME13'),
            ('Spine', 'THEME05'),
            ('FK_L', 'THEME09'),
            ('FK_R', 'THEME02'),
            ('IK_L', 'THEME03'),
            ('IK_R', 'THEME04'),
        ]
        self.gizmos = (gizmos_mhx.asString() + gizmos_general.asString())

        self.objectProps = [("MhxRig", '"MHX"')]
        self.armatureProps = []
        self.headName = 'head'
        self.master = 'master'

        if amt.options.useMuscles:
            self.vertexGroupFiles = ["head", "muscles", "hand"]
        else:
            self.vertexGroupFiles = ["head", "bones", "hand"]
        """
        if options.skirtRig == "own":
            self.vertexGroupFiles.append("skirt-rigged")
        elif options.skirtRig == "inh":
            self.vertexGroupFiles.append("skirt")

        if options.maleRig:
            self.vertexGroupFiles.append( "male" )
        """

        self.joints = (
            rig_joints.Joints +
            rig_master.Joints +
            rig_bones.Joints +
            rig_muscle.Joints +
            rig_mhx.Joints +
            rig_face.Joints
        )

        self.headsTails = mergeDicts([
            rig_master.HeadsTails,
            rig_bones.HeadsTails,
            rig_muscle.HeadsTails,
            rig_mhx.HeadsTails,
            rig_face.HeadsTails
        ])

        self.constraints = mergeDicts([
            rig_bones.Constraints,
            rig_muscle.Constraints,
            rig_mhx.Constraints,
            rig_face.Constraints
        ])

        self.rotationLimits = mergeDicts([
            rig_bones.RotationLimits,
            rig_muscle.RotationLimits,
            rig_mhx.RotationLimits,
            rig_face.RotationLimits
        ])

        self.customShapes = mergeDicts([
            rig_master.CustomShapes,
            rig_bones.CustomShapes,
            rig_muscle.CustomShapes,
            rig_mhx.CustomShapes,
            rig_face.CustomShapes
        ])

        self.parents = rig_mhx.Parents


    def createBones(self, boneInfo):
        generic = mergeDicts([rig_master.Armature, rig_bones.Armature, rig_face.Armature])
        self.addBones(rig_master.Armature, boneInfo)
        self.addBones(rig_bones.Armature, boneInfo)
        self.addBones(rig_face.Armature, boneInfo)
        self.addDeformBones(generic, boneInfo),
        self.addBones(rig_muscle.Armature, boneInfo)
        self.addBones(rig_mhx.Armature, boneInfo)
        self.addIkChains(generic, boneInfo, rig_mhx.IkChains)
        PythonParser.createBones(self, boneInfo)


    def dynamicLocations(self):
        return
        rig_body.DynamicLocations()


