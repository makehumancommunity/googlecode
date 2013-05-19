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
from collections import OrderedDict
import mh2proxy
import exportutils

import armature as amtpkg
from .flags import *
from armature.rigdefs import CArmature

from . import posebone
from . import mhx_drivers
from . import mhx_constraints
from . import rig_joints
from . import rig_master
from . import rig_bones
from . import rig_muscle
from . import rig_face
from . import rig_mhx


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
    
    setupCircle(fp, "GZM_Circle01", 0.1)
    setupCircle(fp, "GZM_Circle025", 0.25)
    setupCircle(fp, "GZM_Circle05", 0.5)
    setupCircle(fp, "GZM_Circle10", 1.0)
    setupCircle(fp, "GZM_Circle15", 1.5)
    setupCircle(fp, "GZM_Circle20", 2.0)
    setupCube(fp, "GZM_Cube01", 0.1, 0)
    setupCube(fp, "GZM_Cube025", 0.25, 0)
    setupCube(fp, "GZM_Cube05", 0.5, 0)
    setupCube(fp, "GZM_EndCube01", 0.1, 1)
    setupCube(fp, "GZM_Chest", (0.7,0.25,0.5), (0,0.5,0.35))
    setupCube(fp, "GZM_Root", (1.25,0.5,1.0), 1)
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
        self.master = None
        self.parents = {}
        self.boneLayers = "00000001"
        self.useDeformBones = False
        self.splitBones = {}

        self.bones = OrderedDict()
        self.bbones = {}
        self.boneGroups = []
        self.rotationLimits = {}
        self.customShapes = {}
        self.constraints = {}
        self.recalcRoll = []              
        self.vertexGroupFiles = []
        self.gizmoFiles = []
        self.headName = 'Head'
        self.objectProps = [("MhxRig", '"%s"' % config.rigtype)]
        self.armatureProps = []
        self.customProps = []


    def distance(self, joint1, joint2):
        vec = self.locations[joint2] - self.locations[joint1]
        return math.sqrt(np.dot(vec,vec))
        
        
    def addIkChains(self, boneInfo, bones, ikChains):
        for bone,data in boneInfo.items():
            (roll, parent, flags, layers) = data
            headTail = self.headsTails[bone]
            base,ext = splitBoneName(bone)
            parent = safeGet(self.parents, bone, parent)
            nodef = flags & ~F_DEF
            data = (roll, parent, nodef, L_HELP)

            if base in ikChains.keys():      
                value = ikChains[base]
                fkbone = base + ".fk" + ext
                ikbone = base + ".ik" + ext
                self.headsTails[fkbone] = headTail
                self.headsTails[ikbone] = headTail
                
                try:
                    layer,cnsname = value
                    simple = True
                except:
                    count, layer, cnsname, target, pole, poleAngle, rang = value
                    simple = False
                
                if simple:
                    if ext == ".R":
                        layer <<= 16
                    bones[bone] = data
                    bones[fkbone] = (roll, parent, nodef, layer<<1)
                    bones[ikbone] = (roll, parent, nodef, layer)
                    self.constraints[bone] = [
                        copyTransform(fkbone, cnsname+"FK"), 
                        copyTransform(ikbone, cnsname+"IK", 0)
                    ]
                    
                elif isinstance(value, tuple):
                    words = parent.rsplit(".", 1)
                    pbase = words[0]
                    if len(words) == 1:
                        pext = ""
                    else:
                        pext = "." + words[1]                
                    fkParent = pbase + ".fk" + pext
                    ikParent = pbase + ".ik" + pext
                    if ext == ".R":
                        layer <<= 16
                        poleAngle = rang
                    bones[bone] = data
                    bones[fkbone] = (roll, fkParent, nodef, layer<<1)
                    bones[ikbone] = (roll, ikParent, nodef, layer)
                    self.constraints[bone] = [
                        copyTransform(fkbone, cnsname+"FK"), 
                        copyTransform(ikbone, cnsname+"IK", 0)
                    ]        
                    ikTarget = target + ".ik" + ext
                    poleTarget = pole + ".ik" + ext
                    self.constraints[ikbone] = [
                        ('IK', 0, 1, ['IK', ikTarget, count, (poleAngle, poleTarget), (True, False,False)])
                    ]                        

            else:
                bones[bone] = (roll, parent, nodef, layers)


    def addDeformBones(self, boneInfo, bones):
        for bone,data in boneInfo.items():
            (roll, parent, flags, layers) = data
            if flags & F_DEF == 0:
                print "Skip", bone
                continue
            headTail = self.headsTails[bone]
            base,ext = splitBoneName(bone)
            parent = safeGet(self.parents, bone, parent)
                
            if parent and self.useDeformBones:
                pbase, pext = splitBoneName(parent)
                if pbase in self.splitBones:
                    defParent = "DEF-"+pbase+".3"+pext
                else:
                    try:
                        parInfo = boneInfo[parent]
                    except KeyError:
                        parInfo = None                        
                    if parInfo and (parInfo[2] & F_DEF):
                        defParent = "DEF-"+parent
                    else:
                        defParent = parent
            else:
                defParent = parent             
                
            if base in self.splitBones.keys(): 
                defname1 = "DEF-"+base+".1"+ext
                defname2 = "DEF-"+base+".2"+ext
                defname3 = "DEF-"+base+".3"+ext
                head,tail = headTail
                self.headsTails[defname1] = (head, ((0.667,head),(0.333,tail)))
                self.headsTails[defname2] = (((0.667,head),(0.333,tail)), ((0.333,head),(0.667,tail)))
                self.headsTails[defname3] = (((0.333,head),(0.667,tail)), tail)
                bones[defname1] = (roll, defParent, F_DEF+F_CON, L_DEF)
                bones[defname3] = (roll, bone, F_DEF, L_DEF)
                bones[defname2] = (roll, defParent, F_DEF, L_DEF)
                fkbone = base + ".fk" + ext
                ikbone = base + ".ik" + ext
                child = self.splitBones[base]
                self.constraints[defname1] = [
                    ('IK', 0, 1, ['IK', child+ext, 1, None, (True, False,True)])
                ]
                self.constraints[defname2] = [
                    ('CopyLoc', 0, 1, ["CopyLoc", defname1, (1,1,1), (0,0,0), 1, False]),
                    ('CopyRot', 0, 1, [defname1, defname1, (1,1,1), (0,0,0), False]),
                    ('CopyRot', 0, 0.5, [bone, bone, (1,1,1), (0,0,0), False])
                ]

            elif self.useDeformBones:
                defname = "DEF-"+bone
                self.headsTails[defname] = headTail
                bones[defname] = (roll, defParent, F_DEF, L_DEF)
                self.constraints[defname] = [copyTransform(bone, bone)]
                
        return bones           
 

    def renameVertexGroups(self, vgroups):
        if self.useDeformBones:
            ngroups = []
            for bone,vgroup in vgroups:
                base = splitBoneName(bone)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bone, vgroup, ngroups)
                else:
                    defname = "DEF-"+bone
                    try:
                        bones[defname]
                        ngroups.append((defname,vgroup))
                    except KeyError:
                        ngroups.append((bone,vgroup))
            return ngroups
        elif self.splitBones:
            ngroups = []
            for bone,vgroup in vgroups:
                base = splitBoneName(bone)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bone, vgroup, ngroups)
                else:
                    ngroups.append((bone,vgroup))
            return ngroups
        else:
            return vgroups


    def splitVertexGroup(self, bone, vgroup, ngroups):
        base,ext = splitBoneName(bone)
        defname1 = "DEF-"+base+".1"+ext
        defname2 = "DEF-"+base+".2"+ext
        defname3 = "DEF-"+base+".3"+ext
        hname,tname = self.headsTails[bone]
        head = self.locations[hname]
        tail = self.locations[tname]
        orig = head + self.origin
        vec0 = tail - head
        vec = vec0/np.dot(vec0,vec0)
        
        vgroup1 = []
        vgroup2 = []
        vgroup3 = []
        for vn,w in vgroup:
            y = self.mesh.coord[vn] - orig
            x = np.dot(vec,y)
            if False:
                print(bone, vn)
                print(self.mesh.coord[vn])
                print(orig)
                print(head)
                print(tail)
                print(vec0)
                print(vec)
                print(x)
                print(y)
                halt
            if x < 0:
                vgroup1.append((vn,w))
            elif x < 0.5:
                vgroup1.append((vn, (1-2*x)*w))
                vgroup2.append((vn, (2*x)*w))
            elif x < 1:
                vgroup2.append((vn, (2-2*x)*w))
                vgroup3.append((vn, (2*x-1)*w))
            else:
                vgroup3.append((vn,w))
        
        ngroups += [(defname1,vgroup1), (defname2,vgroup2), (defname3,vgroup3)]
        
    
    def setup(self):
        if self.rigtype in ["mhx", "basic", "rigify"]:
            self.setupJoints()       
            self.moveOriginToFloor()
            self.dynamicLocations()
            for bone in self.bones.keys():
                head,tail = self.headsTails[bone]
                self.rigHeads[bone] = self.findLocation(head)
                self.rigTails[bone] = self.findLocation(tail)
        else:
            self.joints += rig_joints.DeformJoints + rig_joints.FloorJoints
            self.setupJoints()
            self.moveOriginToFloor()
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
        


    def setupJoints (self):
        """
        Evaluate symbolic expressions for joint locations and store them in self.locations.
        Joint locations are specified symbolically in the *Joints list in the beginning of the
        rig_*.py files (e.g. ArmJoints in rig_arm.py). 
        """
        
        for (key, typ, data) in self.joints:
            if typ == 'j':
                loc = mh2proxy.calcJointPos(self.mesh, data)
                self.locations[key] = loc
                self.locations[data] = loc
            elif typ == 'v':
                v = int(data)
                self.locations[key] = self.mesh.coord[v]
            elif typ == 'x':
                self.locations[key] = np.array((float(data[0]), float(data[2]), -float(data[1])))
            elif typ == 'vo':
                v = int(data[0])
                offset = np.array((float(data[1]), float(data[3]), -float(data[2])))
                self.locations[key] = self.mesh.coord[v] + offset
            elif typ == 'vl':
                ((k1, v1), (k2, v2)) = data
                loc1 = self.mesh.coord[int(v1)]
                loc2 = self.mesh.coord[int(v2)]
                self.locations[key] = k1*loc1 + k2*loc2
            elif typ == 'f':
                (raw, head, tail, offs) = data
                rloc = self.locations[raw]
                hloc = self.locations[head]
                tloc = self.locations[tail]
                vec = tloc - hloc
                vraw = rloc - hloc
                x = np.dot(vec, vraw)/np.dot(vec,vec)
                self.locations[key] = hloc + x*vec + np.array(offs)
            elif typ == 'b':
                self.locations[key] = self.locations[data]
            elif typ == 'p':
                x = self.locations[data[0]]
                y = self.locations[data[1]]
                z = self.locations[data[2]]
                self.locations[key] = np.array((x[0],y[1],z[2]))
            elif typ == 'vz':
                v = int(data[0])
                z = self.mesh.coord[v][2]
                loc = self.locations[data[1]]
                self.locations[key] = np.array((loc[0],loc[1],z))
            elif typ == 'X':
                r = self.locations[data[0]]
                (x,y,z) = data[1]
                r1 = np.array([float(x), float(y), float(z)])
                self.locations[key] = np.cross(r, r1)
            elif typ == 'l':
                ((k1, joint1), (k2, joint2)) = data
                self.locations[key] = k1*self.locations[joint1] + k2*self.locations[joint2]
            elif typ == 'o':
                (joint, offsSym) = data
                if type(offsSym) == str:
                    offs = self.locations[offsSym]
                else:
                    offs = np.array(offsSym)
                self.locations[key] = self.locations[joint] + offs
            else:
                raise NameError("Unknown %s" % typ)
        return
    
    
    def moveOriginToFloor(self):
        if self.config.feetOnGround:
            self.origin = self.locations['floor']
            for key in self.locations.keys():
                self.locations[key] = self.locations[key] - self.origin
        else:
            self.origin = np.array([0,0,0], float)
        return
    
        
    def setupHeadsTails(self):
        self.rigHeads = {}
        self.rigTails = {}
        scale = self.config.scale
        for (bone, head, tail) in self.headsTails:
            self.rigHeads[bone] = findLocation(self, head)
            self.rigTails[bone] = findLocation(self, tail)
        
    
    def findLocation(self, joint):
        if isinstance(joint, str):
            return self.locations[joint]
        else:
            (first, second) = joint
            if isinstance(first, str):
                return self.locations[first] + second
            else:
                w1,j1 = first
                w2,j2 = second
                return w1*self.locations[j1] + w2*self.locations[j2]



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


    def writeEditBones(self, fp):        
        for bone,data in self.bones.items():
            (roll, parent, flags, layers) = data
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


    def sortBones(self, bones):
        children = {}
        roots = []
        for bone in bones.keys():
            children[bone] = []
        for bone,data in bones.items():
            parent = data[1]
            if parent:
                children[parent].append(bone)
            elif self.master:
                if bone == self.master:
                    roots.append(bone)
                else:
                    (roll, parent, flags, layers) = data
                    bones[bone] = (roll, self.master, flags, layers)
                    children[self.master].append(bone)
            else:
                roots.append(bone)
        for root in roots:            
            self.sortBones1(root, bones, children)


    def sortBones1(self, bone, bones, children):
        self.bones[bone] = bones[bone]
        for child in children[bone]:
            self.sortBones1(child, bones, children)
        
    
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

    def dynamicLocations(self):
        pass
        

#-------------------------------------------------------------------------------        
#   MHX armature
#-------------------------------------------------------------------------------        

class MhxArmature(ExportArmature):

    def __init__(self, name, human, config):    
        import gizmos_mhx, gizmos_general
    
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = 'mhx'
        self.boneLayers = "0068056b"
        self.useDeformBones = True
        self.splitBones = rig_mhx.SplitBones

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
        self.preservevolume = False
        
        self.vertexGroupFiles = ["head", "bones", "palm", "tight"]
        if config.skirtRig == "own":
            self.vertexGroupFiles.append("skirt-rigged")    
        elif config.skirtRig == "inh":
            self.vertexGroupFiles.append("skirt")    

        if config.maleRig:
            self.vertexGroupFiles.append( "male" )
                                                        
        self.joints = (
            rig_joints.DeformJoints +
            rig_joints.FloorJoints +
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
        
        generic = mergeDicts([rig_bones.Armature, rig_face.Armature])
        bones = {}
        addBones(rig_bones.Armature, bones)
        self.addDeformBones(generic, bones),
        addBones(rig_muscle.Armature, bones)
        addBones(rig_mhx.Armature, bones)
        self.addIkChains(self, rig_bones.Armature, bones, rig_mhx.IkChains)
        addBones(rig_face.Armature, bones)
        sortBones(bones)
        
        return

        if config.skirtRig == "own":
            self.joints += rig_skirt.Joints
            self.headsTails += rig_skirt.HeadsTails
            self.boneDefs += rig_skirt.Armature        

        if config.maleRig:
            self.boneDefs += rig_body.MaleArmature        

        if self.config.facepanel:            
            self.joints += rig_panel.Joints
            self.headsTails += rig_panel.HeadsTails
            self.boneDefs += rig_panel.Armature

        if False and config.custom:
            (custJoints, custHeadsTails, custArmature, self.customProps) = exportutils.custom.setupCustomRig(config)
            self.joints += custJoints
            self.headsTails += custHeadsTails
            self.boneDefs += custArmature
        

    def dynamicLocations(self):
        return
        rig_body.DynamicLocations()
        

    def setupCustomShapes(self, fp):
        ExportArmature.setupCustomShapes(self, fp)
        if self.config.facepanel:
            import gizmos_panel
            setupCube(fp, "MHCube025", 0.25, 0)
            setupCube(fp, "MHCube05", 0.5, 0)
            self.gizmos = gizmos_panel.asString()
            fp.write(self.gizmos)
        

    def writeControlPoses(self, fp, config):
        self.writeBoneGroups(fp)   
        ExportArmature.writeControlPoses(self, fp, config)


    def writeDrivers(self, fp):
        driverList = (
            #mhx_drivers.writePropDrivers(fp, self, rig_mhx.PropDrivers, "", "Mha") +
            mhx_drivers.writePropDrivers(fp, self, rig_mhx.PropLRDrivers, "L", "Mha") +
            mhx_drivers.writePropDrivers(fp, self, rig_mhx.PropLRDrivers, "R", "Mha") +
            mhx_drivers.writePropDrivers(fp, self, rig_face.PropDrivers, "", "Mha") +
            mhx_drivers.writeDrivers(fp, True, rig_face.DeformDrivers(fp, self))            
        )
        return driverList

        if self.config.advancedSpine:
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

        if self.config.advancedSpine:
        
            fp.write("""
  Property MhaSpineInvert False Spine_from_shoulders_to_pelvis ;
  PropKeys MhaSpineInvert "type":'BOOLEAN',"min":0,"max":1, ;
  
  Property MhaSpineIk False Spine_FK/IK ;
  PropKeys MhaSpineIk "type":'BOOLEAN',"min":0,"max":1, ;
  
  Property MhaSpineStretch 0.2 Spine_stretch_amount ;
  PropKeys MhaSpineStretch "min":0.0,"max":1.0, ;    
""")        

#-------------------------------------------------------------------------------        
#   Basic armature
#-------------------------------------------------------------------------------        

class BasicArmature(ExportArmature):

    def __init__(self, name, human, config):   
        import gizmos_general
        
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = "basic"
        self.boneLayers = "08a80caa"

        self.vertexGroupFiles = ["head", "basic"]
        self.gizmos = gizmos_general.asString()
        self.master = 'master'
        self.headName = 'head'
        self.preservevolume = True
        self.useDeformBones = False
        self.splitBones = rig_mhx.SplitBones
            
        self.joints = (
            rig_master.DeformJoints +
            rig_joints.FloorJoints +
            rig_bones.Joints +
            rig_bones.Joints +
            rig_muscle.Joints +
            rig_face.Joints
        )
        
        self.headsTails = mergeDicts([
            rig_master.HeadsTails,
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
            rig_master.CustomShapes,
            rig_bones.CustomShapes,
            rig_muscle.CustomShapes,
            rig_face.CustomShapes
        ])

        bones = {}
        addBones(rig_master.Armature, bones)
        addBones(rig_bones.Armature, bones)
        self.addDeformBones(rig_bones.Armature, bones),
        addBones(rig_muscle.Armature, bones)
        addBones(rig_face.Armature, bones)
        self.sortBones(bones)
        
        self.objectProps = rig_bones.ObjectProps
        self.armatureProps = rig_bones.ArmatureProps
        

    def writeDrivers(self, fp):
        rig_face.DeformDrivers(fp, self)        
        mhx_drivers.writePropDrivers(fp, self, rig_face.PropDrivers, "", "Mha")
        mhx_drivers.writePropDrivers(fp, self, rig_face.SoftPropDrivers, "", "Mha")
        return []


class RigifyArmature(BasicArmature):

    def __init__(self, name, human, config):   
        BasicArmature. __init__(self, name, human, config)
        self.rigtype = 'rigify'
        self.master = None
        self.useCustomShapes = False
        self.objectProps += [("MhxRig", '"Rigify"')]
        self.gizmos = None
        
        bones = {}
        addBones(rig_bones.Armature, bones)
        addBones(rig_muscle.Armature, bones)
        addBones(rig_face.Armature, bones)
        self.sortBones(bones)
        
        
#-------------------------------------------------------------------------------        
#   Utilities
#-------------------------------------------------------------------------------        

def splitBoneName(bone):
    words = bone.rsplit(".", 1)
    if len(words) > 1:
        return words[0], "."+words[1]
    else:
        return words[0], ""
       

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


       
