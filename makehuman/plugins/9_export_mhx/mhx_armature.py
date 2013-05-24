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
import mh2proxy
import exportutils

import armature
from armature.flags import *
from armature.python import PythonArmature
from armature import rig_joints
from armature import rig_bones

from . import posebone
from . import mhx_drivers
from . import mhx_constraints
    
#-------------------------------------------------------------------------------        
#   Armature selector
#-------------------------------------------------------------------------------        

def getArmature(name, human, config):        
    if config.rigtype == 'mhx':
        from . import amt_mhx
        return amt_mhx.MhxArmature(name, human, config)
    elif config.rigtype == 'basic':
        from . import amt_basic
        return amt_basic.BasicArmature(name, human, config)
    elif config.rigtype == 'rigify':
        from . import amt_rigify
        return amt_rigify.RigifyArmature(name, human, config)
    else:
        return ExportArmature(name, human, config)

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


def setupSimpleCustomShapes(fp):
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

#-------------------------------------------------------------------------------        
#   Armature used for export
#-------------------------------------------------------------------------------        

class ExportArmature(PythonArmature):

    def __init__(self, name, human, config):    
        PythonArmature. __init__(self, name, human, config)
        self.customShapeFiles = []
        self.customShapes = {}
        self.gizmos = None
        self.master = None


    def setupCustomShapes(self, fp):
        fp.write(
            "Object CustomShapes EMPTY None\n" +
            "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
            "end Object\n\n")

        if self.gizmos:
            fp.write(self.gizmos)
            setupSimpleCustomShapes(fp)
        else:   
            for (name, data) in self.customShapes.items():
                (typ, r) = data
                if typ == "-circ":
                    setupCircle(fp, name, 0.1*r)
                elif typ == "-box":
                    setupCube(fp, name, 0.1*r, (0,0,0))
                else:
                    halt


    def writeEditBones(self, fp):        
        for bone,data in self.bones.items():
            (_roll, parent, flags, layers) = data
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
                
            roll = self.rigRolls[bone]
            if isinstance(roll, str):
                roll = self.rigRolls[roll]
                
            fp.write(
                "    roll %.6g ; \n" % (roll) +
                "    use_connect %s ; \n" % (conn) +
                "    use_deform %s ; \n" % (deform) +
                "    show_wire %s ; \n" % (wire))
    
            if 1 and (flags & F_HID):
                fp.write("    hide True ; \n")
    
            if 0 and self.bbones[bone]:
                (bin, bout, bseg) = self.bbones[bone]
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

    
    def writeControlPoses(self, fp, config):
        # For mhx, basic, rigify        
        for bone in self.bones.keys():
            constraints = safeGet(self.constraints, bone, [])
            customShape = safeGet(self.customShapes, bone, None)
            boneGroup = None
            limit = safeGet(self.rotationLimits, bone, None)
            lockLoc = (0,0,0)
            lockRot = (0,0,0)
            lockScale = (0,0,0)
            ik_dof = (1,1,1)
            flags = 0
            posebone.addPoseBone(fp, self, bone, customShape, boneGroup, lockLoc, lockRot, lockScale, ik_dof, flags, constraints)         
    
        # For other rigs
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
            self.defProp(fp, "FLOAT", key, val, string, min, max)
    
        if self.config.expressions:
            fp.write("#if toggle&T_Shapekeys\n")
            for skey in exportutils.shapekeys.ExpressionUnits:
                self.defProp(fp, "FLOAT", "Mhs%s"%skey, 0.0, skey, -1.0, 2.0)
                #fp.write("  DefProp Float Mhs%s 0.0 %s min=-1.0,max=2.0 ;\n" % (skey, skey))
            fp.write("#endif\n")   


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
        self.writeHideProp(fp, self.name)
        for proxy in self.proxies.values():
            self.writeHideProp(fp, proxy.name)
        if self.config.useCustomShapes: 
            exportutils.custom.listCustomFiles(self.config)                    
        for path,name in self.config.customShapeFiles:
            self.defProp(fp, "FLOAT", name, 0, name[3:], -1.0, 2.0)
            #fp.write("  DefProp Float %s 0 %s  min=-1.0,max=2.0 ;\n" % (name, name[3:]))
  
        fp.write("""
end Object
""")


    def writeHideProp(self, fp, name):                
        self.defProp(fp, "BOOLEAN", "Mhh%s"%name, False, "Control_%s_visibility"%name)
        #fp.write("  DefProp Bool Mhh%s False Control_%s_visibility ;\n" % (name, name))
        return
        
        
#-------------------------------------------------------------------------------        
#   Utilities
#-------------------------------------------------------------------------------        

def m2b(vec):
    return np.array((vec[0], -vec[2], vec[1]))
        
def b2m(vec):
    return np.array((vec[0], vec[2], -vec[1]))
            
def getUnitVector(vec):
    length = math.sqrt(np.dot(vec,vec))
    if length > 1e-6:
        return vec/length
    else:
        return None


def splitBoneName(bone):
    words = bone.rsplit(".", 1)
    if len(words) > 1:
        return words[0], "."+words[1]
    else:
        return words[0], ""
       

def splitBonesNames(base, ext, numAfter):
    if numAfter:
        defname1 = "DEF-"+base+ext+".01"
        defname2 = "DEF-"+base+ext+".02"
        defname3 = "DEF-"+base+ext+".03"
    else:
        defname1 = "DEF-"+base+".01"+ext
        defname2 = "DEF-"+base+".02"+ext
        defname3 = "DEF-"+base+".03"+ext
    return defname1, defname2, defname3


def addBones(dict, bones):
    for key,value in dict.items():
        bones[key] = value


def mergeDicts(dicts):
    bones = {}
    for dict in dicts:   
        addBones(dict, bones)
    return bones
    
    
def safeGet(dict, key, default):
    try:
        return dict[key]
    except KeyError:
        return default
       

def copyTransform(target, cnsname, inf=1):
    return ('CopyTrans', 0, inf, [cnsname, target, 0])


def checkOrthogonal(mat):
    prod = np.dot(mat, mat.transpose())
    diff = prod - np.identity(3,float)
    sum = 0
    for i in range(3):
        for j in range(3):
            if abs(diff[i,j]) > 1e-5:
                raise NameError("Not ortho: diff[%d,%d] = %g\n%s\n\%s" % (i, j, diff[i,j], mat, prod))
    return True

   

       
