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
from armature.python_amt import *
from armature.rigfile_amt import RigfileArmature
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
        return RigfileExportArmature(name, human, config)

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

class ExportArmature:

    def __init__(self, config):
        self.boneLayers = "00000001"
        self.scale = config.scale
        self.proxies = {}

        self.gizmos = None
        self.gizmoFiles = []
        self.recalcRoll = []
        self.objectProps = [("MhxRig", '"%s"' % config.rigtype)]
        self.armatureProps = []
        self.customProps = []
        self.bbones = {}
        self.boneGroups = []
        self.poseInfo = {}


    def setup(self):
        if self.config.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = proxy.getCoords()
                    self.fromRigFile(proxy.rig, amt.human.meshData, coord=coord)
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    #appendRigBones(boneList, proxy.name, L_CLO, body, amt)


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


    def writeControlPoses(self, fp, config):
        # For mhx, basic, rigify
        for bone in self.bones.values():
            posebone.addPoseBone(
                fp, self, bone.name,
                bone.customShape, bone.group,
                bone.lockLocation, bone.lockRotation, bone.lockScale,
                bone.ikDof, bone.flags, bone.constraints)

        # For other rigs
        for (bname, cinfo) in self.poseInfo.items():
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
            posebone.addPoseBone(fp, self, bname, cs, None, (0,0,0), (0,0,0), (1,1,1), (1,1,1), 0, constraints)


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


class PythonExportArmature(PythonArmature, ExportArmature):
    def __init__(self, name, human, config):
        PythonArmature. __init__(self, name, human, config)
        ExportArmature.__init__(self, config)

    def setup(self):
        PythonArmature.setup(self)
        ExportArmature.setup(self)


class RigfileExportArmature(RigfileArmature, ExportArmature):
    def __init__(self, name, human, config):
        RigfileArmature. __init__(self, name, human, config)
        ExportArmature.__init__(self, config)

    def setup(self):
        RigfileArmature.setup(self)
        ExportArmature.setup(self)



