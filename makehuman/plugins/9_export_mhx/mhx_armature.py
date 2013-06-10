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

import math
import numpy as np
import transformations as tm
from collections import OrderedDict
import exportutils
import log

from armature.armature import Armature

from . import posebone
from . import mhx_drivers
from . import mhx_constraints

#-------------------------------------------------------------------------------
#   Setup Armature
#-------------------------------------------------------------------------------

def setupArmature(name, human, options):
    from armature.python_amt import PythonParser
    if options is None:
        return None
    else:
        amt = ExportArmature(name, options)
        amt.parser = PythonParser(amt, human)
        amt.setup()
        log.message("Using rig with options %s" % options)
        return amt

#-------------------------------------------------------------------------------
#   Armature used for mhx export
#-------------------------------------------------------------------------------

class ExportArmature(Armature):

    def __init__(self, name, options):
        Armature.__init__(self, name, options)
        self.visibleLayers = "00000001"
        self.scale = options.scale

        self.recalcRoll = []
        self.objectProps = [("MhxRig", '"MHX"')]
        self.armatureProps = []
        self.customProps = []
        self.bbones = {}
        self.boneGroups = []
        self.poseInfo = {}


        self.visibleLayers = "0068056b"
        self.recalcRoll = []
        self.objectProps = [("MhxRig", '"MHX"')]


    def writeDrivers(self, fp):
        parser = self.parser
        if parser.lrDrivers or parser.drivers:
            fp.write("AnimationData %s True\n" % self.name)
            mhx_drivers.writePropDrivers(fp, self, parser.lrDrivers, "L", "Mha")
            mhx_drivers.writePropDrivers(fp, self, parser.lrDrivers, "R", "Mha")
            mhx_drivers.writeDrivers(fp, True, parser.drivers)

            fp.write(
"""
  action_blend_type 'REPLACE' ;
  action_extrapolation 'HOLD' ;
  action_influence 1 ;
  use_nla True ;
end AnimationData
""")


    def writeActions(self, fp):
        #rig_arm.WriteActions(fp)
        #rig_leg.WriteActions(fp)
        #rig_finger.WriteActions(fp)
        return


    def setup(self):
        Armature.setup(self)

        if self.options.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = proxy.getCoords()
                    self.fromRigFile(proxy.rig, env.human.meshData, coord=coord)
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    #appendRigBones(boneList, proxy.name, L_CLO, body, amt)


    def setupCustomShapes(self, fp):
        import gizmos_mhx, gizmos_general
        gizmos = (gizmos_mhx.asString() + gizmos_general.asString())

        writeCustomEmpty(fp)
        fp.write(gizmos)
        setupSimpleCustomTargets(fp)
        if self.options.facepanel:
            import gizmos_panel
            setupCube(fp, "MHCube025", 0.25, 0)
            setupCube(fp, "MHCube05", 0.5, 0)
            gizmos = gizmos_panel.asString()
            fp.write(gizmos)


    def writeEditBones(self, fp):
        for bone in self.bones.values():
            scale = self.scale

            fp.write("\n  Bone %s %s\n" % (bone.name, True))
            (x, y, z) = scale*bone.head
            fp.write("    head  %.6g %.6g %.6g  ;\n" % (x,-z,y))
            (x, y, z) = scale*bone.tail
            fp.write("    tail %.6g %.6g %.6g  ;\n" % (x,-z,y))

            if bone.parent:
                fp.write("    parent Refer Bone %s ; \n" % (bone.parent))
                parent = self.bones[bone.parent]
                vec = parent.tail - bone.head
                dist = math.sqrt(np.dot(vec,vec))
                conn = (bone.conn and dist < 1e-5)
                fp.write("    use_connect %s ; \n" % conn)
            else:
                fp.write("    use_connect False ; \n")

            fp.write(
                "    roll %.6g ; \n" % (bone.roll) +
                "    use_deform %s ; \n" % (bone.deform) +
                "    show_wire %s ; \n" % (bone.wire))

            if bone.hide:
                fp.write("    hide True ; \n")

            if 0 and bone.bbone:
                (bin, bout, bseg) = bone.bbone
                fp.write(
                    "    bbone_in %d ; \n" % (bin) +
                    "    bbone_out %d ; \n" % (bout) +
                    "    bbone_segments %d ; \n" % (bseg))

            if bone.norot:
                fp.write("    use_inherit_rotation False ; \n")
            if bone.scale:
                fp.write("    use_inherit_scale True ; \n")
            else:
                fp.write("    use_inherit_scale False ; \n")
            fp.write("    layers Array ")

            bit = 1
            for n in range(32):
                if bone.layers & bit:
                    fp.write("1 ")
                else:
                    fp.write("0 ")
                bit = bit << 1

            fp.write(" ; \n" +
                "    use_local_location %s ; \n" % bone.lloc +
                "    lock %s ; \n" % bone.lock +
                "    use_envelope_multiply False ; \n"+
                "    hide_select %s ; \n" % (bone.restr) +
                "  end Bone \n")


    def writeBoneGroups(self, fp):
        if not fp:
            return
        for (name, color) in self.boneGroups:
            fp.write(
                "    BoneGroup %s\n" % name +
                "      name '%s' ;\n" % name +
                "      color_set '%s' ;\n" % color +
                "    end BoneGroup\n")
        return


    def writeControlPoses(self, fp, options):
        self.writeBoneGroups(fp)

        for bone in self.bones.values():
            posebone.addPoseBone(
                fp, self, bone.name,
                bone.customShape, bone.group,
                bone.lockLocation, bone.lockRotation, bone.lockScale,
                bone.ikDof, bone.flags, bone.constraints)

    def writeProperties(self, fp):
        for (key, val) in self.objectProps:
            fp.write("  Property %s %s ;\n" % (key, val))

        for (key, val, string, min, max) in self.customProps:
            self.defProp(fp, "FLOAT", key, val, string, min, max)

        if self.options.useExpressions:
            fp.write("#if toggle&T_Shapekeys\n")
            for skey in exportutils.shapekeys.ExpressionUnits:
                self.defProp(fp, "FLOAT", "Mhs%s"%skey, 0.0, skey, -1.0, 2.0)
                #fp.write("  DefProp Float Mhs%s 0.0 %s min=-1.0,max=2.0 ;\n" % (skey, skey))
            fp.write("#endif\n")

        fp.write("""
  Property MhaArmIk_L 0.0 Left_arm_FK/IK ;
  PropKeys MhaArmIk_L "min":0.0,"max":1.0, ;

  Property MhaArmHinge_L False Left_arm_hinge ;
  PropKeys MhaArmHinge_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaElbowPlant_L False Left_elbow_plant ;
  PropKeys MhaElbowPlant_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaHandFollowsIKHand_L True Left_hand_follows_wrist ;
  PropKeys MhaHandFollowsIKHand_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegIk_L 0.0 Left_leg_FK/IK ;
  PropKeys MhaLegIk_L "min":0.0,"max":1.0, ;

  Property MhaLegIkToAnkle_L False Left_leg_IK_to_ankle ;
  PropKeys MhaLegIkToAnkle_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsFoot_L True Left_knee_follows_foot ;
  # PropKeys MhaKneeFollowsFoot_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsHip_L False Left_knee_follows_hip ;
  # PropKeys MhaKneeFollowsHip_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaElbowFollowsIKHand_L False Left_elbow_follows_wrist ;
  # PropKeys MhaElbowFollowsIKHand_L "type":'BOOLEAN',"min":0,"max":1, ;

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

  Property MhaHandFollowsIKHand_R True Right_hand_follows_wrist ;
  PropKeys MhaHandFollowsIKHand_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegIkToAnkle_R False Right_leg_IK_to_ankle ;
  PropKeys MhaLegIkToAnkle_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsFoot_R True Right_knee_follows_foot ;
  # PropKeys MhaKneeFollowsFoot_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaKneeFollowsHip_R False Right_knee_follows_hip ;
  # PropKeys MhaKneeFollowsHip_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property MhaElbowFollowsIKHand_R False Right_elbow_follows_wrist ;
  # PropKeys MhaElbowFollowsIKHand_R "type":'BOOLEAN',"min":0,"max":1, ;

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


    def defProp(self, fp, type, key, val, string, min=0, max=1):
        #fp.write("  DefProp %s %s %s %s min=%s,max=%s ;\n" % (type, key, val, string, min, max))
        if type == "BOOLEAN":
            fp.write(
                '  Property %s %s %s ;\n' % (key, val, string) +
                '  PropKeys %s "type":\'%s\', "min":%d,"max":%d, ;\n' % (key, type, min, max))
        elif type == "FLOAT":
            fp.write(
                '  Property %s %.2f %s ;\n' % (key, val, string) +
                '  PropKeys %s "min":%.2f,"max":%.2f, ;\n' % (key, min, max))
        else:
            halt


    def writeArmature(self, fp, version, env):

        fp.write("""
# ----------------------------- ARMATURE --------------------- #

NoScale False ;
""")

        fp.write("Armature %s %s   Normal \n" % (self.name, self.name))
        self.writeEditBones(fp)

        fp.write("""
  show_axes False ;
  show_bone_custom_shapes True ;
  show_group_colors True ;
  show_names False ;
  draw_type 'STICK' ;
  layers Array 1 1 1 1 1 1 1 1  1 1 1 1 1 1 1 1  1 1 1 1 1 1 1 1  1 1 1 1 1 1 1 1  ;
""")

        if self.recalcRoll:
            fp.write("  RecalcRoll %s ;\n" % self.recalcRoll)

        fp.write("""
  layers_protected Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ;
  pose_position 'POSE' ;
  use_mirror_x False ;

end Armature
""")

        fp.write(
            "Object %s ARMATURE %s\n"  % (self.name, self.name) +
            "  Property MhxVersion %d ;\n" % version)

        fp.write("""
  layers Array 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ;
  up_axis 'Z' ;
  show_x_ray True ;
  draw_type 'WIRE' ;
  Property MhxScale theScale ;
  Property MhxVisemeSet 'BodyLanguage' ;

  Property _RNA_UI {} ;
""")

        self.writeProperties(fp)
        self.writeHideProp(fp, self.name)
        for proxy in env.proxies.values():
            self.writeHideProp(fp, proxy.name)
        for path,name in env.customTargetFiles:
            self.defProp(fp, "FLOAT", "Mhc"+name, 0, name, -1.0, 2.0)
            #fp.write("  DefProp Float %s 0 %s  min=-1.0,max=2.0 ;\n" % (name, name[3:]))

        fp.write("""
end Object
""")


    def writeHideProp(self, fp, name):
        self.defProp(fp, "BOOLEAN", "Mhh%s"%name, False, "Control_%s_visibility"%name)
        #fp.write("  DefProp Bool Mhh%s False Control_%s_visibility ;\n" % (name, name))
        return

#-------------------------------------------------------------------------------
#   Setup custom shapes
#-------------------------------------------------------------------------------

def writeCustomEmpty(fp):
    fp.write(
        "Object CustomShapes EMPTY None\n" +
        "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
        "end Object\n\n")


def setupCircle(fp, name, r):
    """
    Write circle object to the MHX file. Circles are used as custom shapes.

    fp:
        *File*: Output file pointer.
    name:
        *string*: Object name.
    r:
        *float*: Radius.
    """

    fp.write("\n"+
        "Mesh %s %s \n" % (name, name) +
        "  Verts\n")
    for n in range(16):
        v = n*pi/8
        y = 0.5 + 0.02*sin(4*v)
        fp.write("    v %.3f %.3f %.3f ;\n" % (r*math.cos(v), y, r*math.sin(v)))
    fp.write(
        "  end Verts\n" +
        "  Edges\n")
    for n in range(15):
        fp.write("    e %d %d ;\n" % (n, n+1))
    fp.write(
        "    e 15 0 ;\n" +
        "  end Edges\n"+
        "end Mesh\n")

    fp.write(
        "Object %s MESH %s\n" % (name, name) +
        "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n"+
        "  parent Refer Object CustomShapes ;\n"+
        "end Object\n")


def setupCube(fp, name, r, offs):
    """
    Write cube object to the MHX file. Cubes are used as custom shapes.

    fp:
        *File*: Output file pointer.
    name:
        *string*: Object name.
    r:
        *float* or *float triple*: Side(s) of cube.
    offs:
        *float* or *float triple*: Y offset or offsets from origin.
    """

    try:
        (rx,ry,rz) = r
    except:
        (rx,ry,rz) = (r,r,r)
    try:
        (dx,dy,dz) = offs
    except:
        (dx,dy,dz) = (0,offs,0)

    fp.write("\n"+
        "Mesh %s %s \n" % (name, name) +
        "  Verts\n")
    for x in [-rx,rx]:
        for y in [-ry,ry]:
            for z in [-rz,rz]:
                fp.write("    v %.2f %.2f %.2f ;\n" % (x+dx,y+dy,z+dz))
    fp.write(
        "  end Verts\n" +
        "  Faces\n" +
        "    f 0 1 3 2 ;\n" +
        "    f 4 6 7 5 ;\n" +
        "    f 0 2 6 4 ;\n" +
        "    f 1 5 7 3 ;\n" +
        "    f 1 0 4 5 ;\n" +
        "    f 2 3 7 6 ;\n" +
        "  end Faces\n" +
        "end Mesh\n")

    fp.write(
        "Object %s MESH %s\n" % (name, name) +
        "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
        "  parent Refer Object CustomShapes ;\n" +
        "end Object\n")


def setupSimpleCustomTargets(fp):
    """
    Write simple custom shapes to the MHX file. Additional custom shapes are defined in
    mhx files in mhx/templates.

    fp:
        *File*: Output file pointer.
    """

    setupCircle(fp, "GZM_Circle01", 0.1)
    setupCircle(fp, "GZM_Circle025", 0.25)
    setupCircle(fp, "GZM_Circle05", 0.5)
    setupCircle(fp, "GZM_Circle10", 1.0)
    setupCircle(fp, "GZM_Circle15", 1.5)
    setupCircle(fp, "GZM_Circle20", 2.0)
    setupCube(fp, "GZM_Cube01", 0.1, 0)
    setupCube(fp, "GZM_Cube025", 0.25, 0)
    setupCube(fp, "GZM_Cube05", 0.5, 0)
    setupCube(fp, "GZM_EndCube025", 0.25, 1)
    setupCube(fp, "GZM_Chest", (0.7,0.25,0.5), (0,0.5,0.35))
    setupCube(fp, "GZM_Root", (1.25,0.5,1.0), 1)

