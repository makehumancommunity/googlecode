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
import mh2proxy
import exportutils

import armature as amtpkg
from armature.flags import *
from armature.rigdefs import CArmature

from . import posebone
from . import rig_body_25
from . import rig_shoulder_25
from . import rig_arm_25
from . import rig_finger_25
from . import rig_leg_25
from . import rig_toe_25
from . import rig_face_25
from . import rig_panel_25
from . import rig_skirt_25
from . import rigify_rig


#-------------------------------------------------------------------------------        
#   Setup custom shapes
#-------------------------------------------------------------------------------        

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


def setupCustomShapes(fp):
    """
    Write simple custom shapes to the MHX file. Additional custom shapes are defined in 
    mhx files in mhx/templates.
    
    fp:
        *File*: Output file pointer. 
    """
    
    setupCircle(fp, "MHCircle01", 0.1)
    setupCircle(fp, "MHCircle025", 0.25)
    setupCircle(fp, "MHCircle05", 0.5)
    setupCircle(fp, "MHCircle10", 1.0)
    setupCircle(fp, "MHCircle15", 1.5)
    setupCircle(fp, "MHCircle20", 2.0)
    setupCube(fp, "MHCube01", 0.1, 0)
    setupCube(fp, "MHCube025", 0.25, 0)
    setupCube(fp, "MHCube05", 0.5, 0)
    setupCube(fp, "MHEndCube01", 0.1, 1)
    setupCube(fp, "MHChest", (0.7,0.25,0.5), (0,0.5,0.35))
    setupCube(fp, "MHRoot", (1.25,0.5,1.0), 1)
    return

#-------------------------------------------------------------------------------        
#   Armature used for export
#-------------------------------------------------------------------------------        

class ExportArmature(CArmature):

    def __init__(self, name, human, config):    
        CArmature. __init__(self, name, human, config)
        self.customShapeFiles = []
        self.customShapes = {}
        self.poseInfo = {}
        self.gizmos = None


    def scanProxies(self):
        self.proxies = {}
        for pfile in self.config.getProxyList():
            if pfile.file:
                print("Scan", pfile, pfile.type)
                proxy = mh2proxy.readProxyFile(self.mesh, pfile, True)
                if proxy:
                    self.proxies[proxy.name] = proxy        


    def setup(self):
        if self.config.facepanel:            
            self.joints += rig_panel_25.PanelJoints
            self.headsTails += rig_panel_25.PanelHeadsTails
            self.boneDefs += rig_panel_25.PanelArmature

        amtpkg.rigdefs.CArmature.setup(self)
        
        if self.config.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = []
                    for refVert in proxy.refVerts:
                        coord.append(refVert.getCoord())
                    (locations, boneList, weights) = exportutils.rig.readRigFile(proxy.rig, amt.mesh, coord=coord) 
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    appendRigBones(boneList, proxy.name, L_CLO, body, amt)
        

    def setupCustomShapes(self, fp):
        if self.gizmos:
            fp.write(self.gizmos)
            setupCustomShapes(fp)
        else:        
            for (name, data) in self.customShapes.items():
                (typ, r) = data
                if typ == "-circ":
                    setupCircle(fp, name, 0.1*r)
                elif typ == "-box":
                    setupCube(fp, name, 0.1*r, (0,0,0))
                else:
                    halt

        if self.config.facepanel:
            import gizmos_panel
            setupCube(fp, "MHCube025", 0.25, 0)
            setupCube(fp, "MHCube05", 0.5, 0)
            self.gizmos = gizmos_panel.asString()
            fp.write(self.gizmos)
        

    def writeEditBones(self, fp):        
        for data in self.boneDefs:
            (bone, roll, parent, flags, layers, bbone) = data
            print(data)
            conn = (flags & F_CON != 0)
            deform = (flags & F_DEF != 0)
            restr = (flags & F_RES != 0)
            wire = (flags & F_WIR != 0)
            lloc = (flags & F_NOLOC == 0)
            lock = (flags & F_LOCK != 0)
            cyc = (flags & F_NOCYC == 0)
        
            scale = self.config.scale
    
            fp.write("\n  Bone %s %s\n" % (bone, True))
            (x, y, z) = scale*self.rigHeads[bone]
            fp.write("    head  %.6g %.6g %.6g  ;\n" % (x,-z,y))
            (x, y, z) = scale*self.rigTails[bone]
            fp.write("    tail %.6g %.6g %.6g  ;\n" % (x,-z,y))
            if type(parent) == tuple:
                (soft, hard) = parent
                if hard:
                    fp.write(
                        "#if toggle&T_HardParents\n" +
                        "    parent Refer Bone %s ;\n" % hard +
                        "#endif\n")
                if soft:
                    fp.write(
                        "#if toggle&T_HardParents==0\n" +
                        "    parent Refer Bone %s ;\n" % soft +
                        "#endif\n")
            elif parent:
                fp.write("    parent Refer Bone %s ; \n" % (parent))
            fp.write(
                "    roll %.6g ; \n" % (roll)+
                "    use_connect %s ; \n" % (conn) +
                "    use_deform %s ; \n" % (deform) +
                "    show_wire %s ; \n" % (wire))
    
            if 1 and (flags & F_HID):
                fp.write("    hide True ; \n")
    
            if bbone:
                (bin, bout, bseg) = bbone
                fp.write(
                    "    bbone_in %d ; \n" % (bin) +
                    "    bbone_out %d ; \n" % (bout) +
                    "    bbone_segments %d ; \n" % (bseg))
    
            if flags & F_NOROT:
                fp.write("    use_inherit_rotation False ; \n")
            if flags & F_SCALE:
                fp.write("    use_inherit_scale True ; \n")
            else:
                fp.write("    use_inherit_scale False ; \n")
            fp.write("    layers Array ")
    
            bit = 1
            for n in range(32):
                if layers & bit:
                    fp.write("1 ")
                else:
                    fp.write("0 ")
                bit = bit << 1
    
            fp.write(" ; \n" +
                "    use_local_location %s ; \n" % lloc +
                "    lock %s ; \n" % lock +
                "    use_envelope_multiply False ; \n"+
                "    hide_select %s ; \n" % (restr) +
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


    def writeControlPoses(self, fp):
        if self.config.facepanel:
            rig_panel_25.PanelControlPoses(fp, self)
            
        for (bone, cinfo) in self.poseInfo.items():
            cs = None
            constraints = []
            for (key, value) in cinfo:
                if key == "CS":
                    cs = value
                elif key == "IK":
                    goal = value[0]
                    n = int(value[1])
                    inf = float(value[2])
                    pt = value[3]
                    if pt:
                        log.debug("%s %s %s %s", goal, n, inf, pt)
                        subtar = pt[0]
                        poleAngle = float(pt[1])
                        pt = (poleAngle, subtar)
                    constraints =  [('IK', 0, inf, ['IK', goal, n, pt, (True,False,True)])]
            posebone.addPoseBone(fp, self, bone, cs, None, (0,0,0), (0,0,0), (1,1,1), (1,1,1), 0, constraints)       


    def writeProperties(self, fp):
        for (key, val) in self.objectProps:
            fp.write("  Property %s %s ;\n" % (key, val))
        for (key, val, string, min, max) in self.customProps:
            fp.write('  DefProp Float Mha%s %.2f %s min=-%.2f,max=%.2f ;\n' % (key, val, string, min, max) )
    
        if self.config.expressions:
            fp.write("#if toggle&T_Shapekeys\n")
            for skey in exportutils.shapekeys.ExpressionUnits:
                fp.write("  DefProp Float Mhs%s 0.0 %s min=-1.0,max=2.0 ;\n" % (skey, skey))
            fp.write("#endif\n")   


    def writeArmature(self, fp, version):
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

        if self.config.rigtype == "mhx":
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
        writeHideProp(fp, self.name)
        for proxy in self.proxies.values():
            writeHideProp(fp, proxy.name)
        if self.config.useCustomShapes: 
            exportutils.custom.listCustomFiles(self.config)                    
        for path,name in self.config.customShapeFiles:
            fp.write("  DefProp Float %s 0 %s  min=-1.0,max=2.0 ;\n" % (name, name[3:]))
  
        fp.write("""
end Object
""")


def writeHideProp(fp, name):                
    fp.write("  DefProp Bool Mhh%s False Control_%s_visibility ;\n" % (name, name))
    return


#-------------------------------------------------------------------------------        
#   MHX armature
#-------------------------------------------------------------------------------        

class MhxArmature(ExportArmature):

    def __init__(self, name, human, config):    
        import gizmos_mhx, gizmos_panel, gizmos_general
    
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = 'mhx'

        self.boneGroups = [
            ('Master', 'THEME13'),
            ('Spine', 'THEME05'),
            ('FK_L', 'THEME09'),
            ('FK_R', 'THEME02'),
            ('IK_L', 'THEME03'),
            ('IK_R', 'THEME04'),
        ]
        self.recalcRoll = "['Foot_L','Toe_L','Foot_R','Toe_R','DfmFoot_L','DfmToe_L','DfmFoot_R','DfmToe_R']"
        self.gizmos = (gizmos_mhx.asString() + gizmos_panel.asString() + gizmos_general.asString())

        self.objectProps = [("MhxRig", '"MHX"')]
        self.armatureProps = []
        self.headName = 'Head'
        self.preservevolume = False
        
        self.vertexGroupFiles = ["head", "bones", "palm", "tight"]
        if config.skirtRig == "own":
            self.vertexGroupFiles.append("skirt-rigged")    
        elif config.skirtRig == "inh":
            self.vertexGroupFiles.append("skirt")    

        if config.maleRig:
            self.vertexGroupFiles.append( "male" )
                                                        
        self.joints = (
            amtpkg.joints.DeformJoints +
            rig_body_25.BodyJoints +
            amtpkg.joints.FloorJoints +
            rig_arm_25.ArmJoints +
            rig_shoulder_25.ShoulderJoints +
            rig_finger_25.FingerJoints +
            rig_leg_25.LegJoints +
            #rig_toe_25.ToeJoints +
            rig_face_25.FaceJoints
        )            
        
        self.headsTails = (
            rig_body_25.BodyHeadsTails +
            rig_shoulder_25.ShoulderHeadsTails +
            rig_arm_25.ArmHeadsTails +
            rig_finger_25.FingerHeadsTails +
            rig_leg_25.LegHeadsTails +
            #rig_toe_25.ToeHeadsTails +
            rig_face_25.FaceHeadsTails
        )

        self.boneDefs = list(rig_body_25.BodyArmature1)
        if config.advancedSpine:
            self.boneDefs += rig_body_25.BodyArmature2Advanced
        else:
            self.boneDefs += rig_body_25.BodyArmature2Simple
        self.boneDefs += rig_body_25.BodyArmature3
        if config.advancedSpine:
            self.boneDefs += rig_body_25.BodyArmature4Advanced
        else:
            self.boneDefs += rig_body_25.BodyArmature4Simple
        self.boneDefs += rig_body_25.BodyArmature5

        self.boneDefs += (
            rig_shoulder_25.ShoulderArmature1 +
            rig_shoulder_25.ShoulderArmature2 +
            rig_arm_25.ArmArmature +            
            rig_finger_25.FingerArmature +
            rig_leg_25.LegArmature +
            #rig_toe_25.ToeArmature +
            rig_face_25.FaceArmature
        )
        
        if config.skirtRig == "own":
            self.joints += rig_skirt_25.SkirtJoints
            self.headsTails += rig_skirt_25.SkirtHeadsTails
            self.boneDefs += rig_skirt_25.SkirtArmature        

        if config.maleRig:
            self.boneDefs += rig_body_25.MaleArmature        

        if False and config.custom:
            (custJoints, custHeadsTails, custArmature, self.customProps) = exportutils.custom.setupCustomRig(config)
            self.joints += custJoints
            self.headsTails += custHeadsTails
            self.boneDefs += custArmature
        

    def dynamicLocations(self):
        rig_body_25.BodyDynamicLocations()
        

    def writeControlPoses(self, fp):
        self.writeBoneGroups(fp)
        rig_body_25.BodyControlPoses(fp, self)
        rig_shoulder_25.ShoulderControlPoses(fp, self)
        rig_arm_25.ArmControlPoses(fp, self)
        rig_finger_25.FingerControlPoses(fp, self)
        rig_leg_25.LegControlPoses(fp, self)
        #rig_toe_25.ToeControlPoses(fp, self)
        rig_face_25.FaceControlPoses(fp, self)
        if self.config.maleRig:
            rig_body_25.MaleControlPoses(fp, self)
        if self.config.skirtRig == "own":
            rig_skirt_25.SkirtControlPoses(fp, self)            
        ExportArmature.writeControlPoses(self, fp)


    def writeDrivers(self, fp):
        driverList = (
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.ArmPropDrivers, "", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.ArmPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.ArmPropLRDrivers, "_R", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.SoftArmPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.SoftArmPropLRDrivers, "_R", "Mha") +
            #writeScriptedBoneDrivers(fp, rig_leg_25.LegBoneDrivers) +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.LegPropDrivers, "", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.LegPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.LegPropLRDrivers, "_R", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.SoftLegPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.SoftLegPropLRDrivers, "_R", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_body_25.BodyPropDrivers, "", "Mha")
        )
        if self.config.advancedSpine:
            driverList += amtpkg.drivers.writePropDrivers(fp, self, rig_body_25.BodyPropDriversAdvanced, "", "Mha") 
        driverList += (
            amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.FacePropDrivers, "", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.SoftFacePropDrivers, "", "Mha")
        )
        fingDrivers = rig_finger_25.getFingerPropDrivers()
        driverList += (
            amtpkg.drivers.writePropDrivers(fp, self, fingDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, fingDrivers, "_R", "Mha") +
            #rig_panel_25.FingerControlDrivers(fp)
            amtpkg.drivers.writeMuscleDrivers(fp, rig_shoulder_25.ShoulderDeformDrivers, self.name) +
            amtpkg.drivers.writeMuscleDrivers(fp, rig_arm_25.ArmDeformDrivers, self.name) +
            amtpkg.drivers.writeMuscleDrivers(fp, rig_leg_25.LegDeformDrivers, self.name)
        )
        faceDrivers = rig_face_25.FaceDeformDrivers(fp, self)
        driverList += amtpkg.drivers.writeDrivers(fp, True, faceDrivers)
        return driverList
    

    def writeActions(self, fp):
        #rig_arm_25.ArmWriteActions(fp)
        #rig_leg_25.LegWriteActions(fp)
        #rig_finger_25.FingerWriteActions(fp)
        return

        
    def writeProperties(self, fp):
        ExportArmature.writeProperties(self, fp)

        fp.write("""
  Property &ArmIk_L 0.0 Left_arm_FK/IK ;
  PropKeys &ArmIk_L "min":0.0,"max":1.0, ;

  Property &ArmHinge_L False Left_arm_hinge ;
  PropKeys &ArmHinge_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property &ElbowPlant_L False Left_elbow_plant ;
  PropKeys &ElbowPlant_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property &HandFollowsWrist_L True Left_hand_follows_wrist ;
  PropKeys &HandFollowsWrist_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property &LegIk_L 0.0 Left_leg_FK/IK ;
  PropKeys &LegIk_L "min":0.0,"max":1.0, ;
  
  Property &LegIkToAnkle_L False Left_leg_IK_to_ankle ;
  PropKeys &LegIkToAnkle_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &KneeFollowsFoot_L True Left_knee_follows_foot ;
  # PropKeys &KneeFollowsFoot_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &KneeFollowsHip_L False Left_knee_follows_hip ;
  # PropKeys &KneeFollowsHip_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &ElbowFollowsWrist_L False Left_elbow_follows_wrist ;
  # PropKeys &ElbowFollowsWrist_L "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &ElbowFollowsShoulder_L True Left_elbow_follows_shoulder ;
  # PropKeys &ElbowFollowsShoulder_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property &FingerControl_L True Left_fingers_controlled ;
  PropKeys &FingerControl_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property &ArmIk_R 0.0 Right_arm_FK/IK ;
  PropKeys &ArmIk_R "min":0.0,"max":1.0, ;

  Property &ArmHinge_R False Right_arm_hinge ;
  PropKeys &ArmHinge_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property &ElbowPlant_R False Right_elbow_plant ;
  PropKeys &ElbowPlant_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property &LegIk_R 0.0 Right_leg_FK/IK ;
  PropKeys &LegIk_R "min":0.0,"max":1.0, ;

  Property &HandFollowsWrist_R True Right_hand_follows_wrist ;
  PropKeys &HandFollowsWrist_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property &LegIkToAnkle_R False Right_leg_IK_to_ankle ;
  PropKeys &LegIkToAnkle_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &KneeFollowsFoot_R True Right_knee_follows_foot ;
  # PropKeys &KneeFollowsFoot_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &KneeFollowsHip_R False Right_knee_follows_hip ;
  # PropKeys &KneeFollowsHip_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &ElbowFollowsWrist_R False Right_elbow_follows_wrist ;
  # PropKeys &ElbowFollowsWrist_R "type":'BOOLEAN',"min":0,"max":1, ;

  # Property &ElbowFollowsShoulder_R True Right_elbow_follows_shoulder ;
  # PropKeys &ElbowFollowsShoulder_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property &GazeFollowsHead 1.0 Gaze_follows_world_or_head ;
  PropKeys &GazeFollowsHead "type":'BOOLEAN',"min":0.0,"max":1.0, ;

  Property &FingerControl_R True Right_fingers_controlled ;
  PropKeys &FingerControl_R "type":'BOOLEAN',"min":0,"max":1, ;
  
  Property &ArmStretch_L 0.1 Left_arm_stretch_amount ;
  PropKeys &ArmStretch_L "min":0.0,"max":1.0, ;

  Property &LegStretch_L 0.1 Left_leg_stretch_amount ;
  PropKeys &LegStretch_L "min":0.0,"max":1.0, ;

  Property &ArmStretch_R 0.1 Right_arm_stretch_amount ;
  PropKeys &ArmStretch_R "min":0.0,"max":1.0, ;

  Property &LegStretch_R 0.1 Right_leg_stretch_amount ;
  PropKeys &LegStretch_R "min":0.0,"max":1.0, ;

  Property &RotationLimits 0.8 Influence_of_rotation_limit_constraints ;
  PropKeys &RotationLimits "min":0.0,"max":1.0, ;

  Property &FreePubis 0.5 Pubis_moves_freely ;
  PropKeys &FreePubis "min":0.0,"max":1.0, ;

  Property &Breathe 0.0 Breathe ;
  PropKeys &Breathe "min":-0.5,"max":2.0, ;
""")

        if self.config.advancedSpine:
        
            fp.write("""
  Property &SpineInvert False Spine_from_shoulders_to_pelvis ;
  PropKeys &SpineInvert "type":'BOOLEAN',"min":0,"max":1, ;
  
  Property &SpineIk False Spine_FK/IK ;
  PropKeys &SpineIk "type":'BOOLEAN',"min":0,"max":1, ;
  
  Property &SpineStretch 0.2 Spine_stretch_amount ;
  PropKeys &SpineStretch "min":0.0,"max":1.0, ;    
""")

        

#-------------------------------------------------------------------------------        
#   Rigify armature
#-------------------------------------------------------------------------------        

class RigifyArmature(ExportArmature):

    def __init__(self, name, human, config):   
        import gizmos_panel, gizmos_rigify
        
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = 'rigify'

        self.vertexGroupFiles = ["head", "rigify"]
        self.gizmos = (gizmos_panel.asString() + gizmos_rigify.asString())
        self.headName = 'head'
        self.preservevolume = True
        faceArmature = swapParentNames(rig_face_25.FaceArmature, 
                           {'Head' : 'head', 'MasterFloor' : None} )
            
        self.joints = (
            amtpkg.joints.DeformJoints +
            rig_body_25.BodyJoints +
            amtpkg.joints.FloorJoints +
            rigify_rig.RigifyJoints +
            rig_face_25.FaceJoints
        )
        
        self.headsTails = (
            rigify_rig.RigifyHeadsTails +
            rig_face_25.FaceHeadsTails
        )

        self.boneDefs = (
            rigify_rig.RigifyArmature +
            faceArmature
        )

        self.objectProps = rigify_rig.RigifyObjectProps + [("MhxRig", '"Rigify"')]
        self.armatureProps = rigify_rig.RigifyArmatureProps


    def writeDrivers(self, fp):
        rig_face_25.FaceDeformDrivers(fp, self)        
        amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.FacePropDrivers, "", "Mha")
        amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.SoftFacePropDrivers, "", "Mha")
        return []


    def writeControlPoses(self, fp):
        rigify_rig.RigifyWritePoses(fp, self)
        rig_face_25.FaceControlPoses(fp, self)
        ExportArmature.writeControlPoses(self, fp)


def swapParentNames(bones, changes):
    nbones = []
    for bone in bones:
        (name, roll, par, flags, level, bb) = bone
        try:
            nbones.append( (name, roll, changes[par], flags, level, bb) )
        except KeyError:
            nbones.append(bone)
    return nbones





