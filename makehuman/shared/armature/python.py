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

Python armature
"""

import math
import numpy as np
import transformations as tm
from collections import OrderedDict
import mh2proxy
import exportutils

from .flags import *
from .rigdefs import CArmature

from . import rig_joints
from . import rig_bones
    
#-------------------------------------------------------------------------------        
#   Python Armature
#-------------------------------------------------------------------------------        

PythonVertexGroupDirectory = "shared/armature/vertexgroups/"

class PythonArmature(CArmature):

    def __init__(self, name, human, config):    
        CArmature. __init__(self, name, human, config)
        self.rigRolls = {}
        self.poseInfo = {}
        self.master = None
        self.parents = {}
        self.boneLayers = "00000001"

        self.useDeformBones = False
        self.useDeformNames = False
        self.useSplitBones = False
        self.splitBones = {}

        self.bones = OrderedDict()
        self.planes = rig_bones.Planes
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
        
        
    def createBones(self, bones):
        """
        config = self.config        
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
        """
        self.sortBones(bones)        
        self.vertexGroupFiles += [PythonVertexGroupDirectory+"leftright"]        
        

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
                    bones[fkbone] = (bone, parent, nodef, layer<<1)
                    bones[ikbone] = (bone, parent, nodef, layer)
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
                    bones[fkbone] = (bone, fkParent, nodef, layer<<1)
                    bones[ikbone] = (bone, ikParent, nodef, layer)
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
        if not (self.useDeformBones or self.useSplitBones):
            return
            
        for bone,data in boneInfo.items():
            (roll, parent, flags, layers) = data
            if flags & F_DEF == 0:
                continue
            headTail = self.headsTails[bone]
            base,ext = splitBoneName(bone)
            parent = safeGet(self.parents, bone, parent)
                
            if parent and self.useDeformBones:
                pbase, pext = splitBoneName(parent)
                if pbase in self.splitBones.keys():
                    npieces = self.splitBones[pbase][0]
                    defParent = "DEF-" + pbase + ".0" + str(npieces) + pext
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
                
            if self.useSplitBones and (base in self.splitBones.keys()): 
                npieces,target,numAfter = self.splitBones[base]
                defname1,defname2,defname3 = splitBonesNames(base, ext, numAfter)
                head,tail = headTail
                fkbone = base + ".fk" + ext
                ikbone = base + ".ik" + ext
                self.constraints[defname1] = [
                    ('IK', 0, 1, ['IK', target+ext, 1, None, (True, False,True)])
                ]
                if npieces == 2:
                    self.headsTails[defname1] = (head, ((0.5,head),(0.5,tail)))
                    self.headsTails[defname2] = (((0.5,head),(0.5,tail)), tail)
                    bones[defname1] = (roll, defParent, F_DEF+F_CON, L_DEF)
                    bones[defname2] = (roll, bone, F_DEF, L_DEF)
                elif npieces == 3:
                    self.headsTails[defname1] = (head, ((0.667,head),(0.333,tail)))
                    self.headsTails[defname2] = (((0.667,head),(0.333,tail)), ((0.333,head),(0.667,tail)))
                    self.headsTails[defname3] = (((0.333,head),(0.667,tail)), tail)
                    bones[defname1] = (bone, defParent, F_DEF+F_CON, L_DEF)
                    bones[defname3] = (bone, bone, F_DEF, L_DEF)
                    bones[defname2] = (bone, defParent, F_DEF, L_DEF)
                    self.constraints[defname2] = [
                        ('CopyLoc', 0, 1, ["CopyLoc", defname1, (1,1,1), (0,0,0), 1, False]),
                        ('CopyRot', 0, 1, [defname1, defname1, (1,1,1), (0,0,0), False]),
                        ('CopyRot', 0, 0.5, [bone, bone, (1,1,1), (0,0,0), False])
                    ]

            elif self.useDeformBones:
                defname = "DEF-"+bone
                self.headsTails[defname] = headTail
                bones[defname] = (bone, defParent, F_DEF, L_DEF)
                self.constraints[defname] = [copyTransform(bone, bone)]
                
        return bones           
 
    
    def getVertexGroups(self):
        vgroupList = []
        for file in self.vertexGroupFiles:
            vgroups = {}
            #file = os.path.join("shared/armature/vertexgroups", name + ".vgrp")
            file = file + ".vgrp"
            fp = open(file, "rU")
            vgroupList = []
            for line in fp:
                words = line.split()
                if len(words) < 2:
                    continue
                elif words[1] == "weights":
                    name = words[2]
                    try:
                        vgroup = vgroups[name]
                    except KeyError:
                        vgroup = []
                        vgroups[name] = vgroup 
                    vgroupList.append((name, vgroup))
                else:
                    vgroup.append((int(words[0]), float(words[1])))
            fp.close()  

        ngroups = OrderedDict([])
        
        if self.useDeformNames:
            for bone,vgroup in vgroupList:
                base = splitBoneName(bone)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bone, vgroup, ngroups)
                elif not self.useSplitBones:
                    defname = "DEF-"+bone
                    ngroups[defname] = vgroup
                else:
                    defname = "DEF-"+bone
                    try:
                        self.bones[defname]
                        ngroups[defname] = vgroup
                    except KeyError:
                        ngroups[bone] = vgroup
            
        elif self.useSplitBones:
            for bone,vgroup in vgroupList:
                base = splitBoneName(bone)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bone, vgroup, ngroups)
                else:
                    ngroups[bone] = vgroup
            
        else:
            for bone,vgroup in vgroupList:
                ngroups[bone] = vgroup

        return ngroups


    def splitVertexGroup(self, bone, vgroup, ngroups):
        base,ext = splitBoneName(bone)
        npieces,target,numAfter = self.splitBones[base]
        defname1,defname2,defname3 = splitBonesNames(base, ext, numAfter)

        hname,tname = self.headsTails[bone]
        head = self.locations[hname]
        tail = self.locations[tname]
        orig = head + self.origin
        vec0 = tail - head
        vec = vec0/np.dot(vec0,vec0)
        
        vgroup1 = []
        vgroup2 = []
        vgroup3 = []
        if npieces == 2:
            for vn,w in vgroup:
                y = self.mesh.coord[vn] - orig
                x = np.dot(vec,y)
                if x < 0:
                    vgroup1.append((vn,w))
                elif x < 0.5:
                    vgroup1.append((vn, (1-x)*w))
                    vgroup2.append((vn, x*w))
                else:
                    vgroup2.append((vn,w))
            ngroups[defname1] = vgroup1
            ngroups[defname2] = vgroup2
        elif npieces == 3:
            for vn,w in vgroup:
                y = self.mesh.coord[vn] - orig
                x = np.dot(vec,y)
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
            ngroups[defname1] = vgroup1
            ngroups[defname2] = vgroup2
            ngroups[defname3] = vgroup3
        
    
    def setup(self):
        if self.rigtype in ["mhx", "basic", "rigify"]:
            self.createBones({})
            self.setupJoints()       
            self.moveOriginToFloor()

            for bone in self.bones.keys():
                head,tail = self.headsTails[bone]
                self.rigHeads[bone] = self.findLocation(head)
                self.rigTails[bone] = self.findLocation(tail)

            normals = {}
            for bone in self.bones.keys():
                (roll, parent, flags, layers) = self.bones[bone]
                if isinstance(roll, str) and roll[0:5] == "Plane":
                    try:
                        normal = normals[roll]
                    except KeyError:
                        normal = None
                    if normal is None:
                        j1,j2,j3 = self.planes[roll]
                        normal = normals[roll] = self.computeNormal(j1, j2, j3)
                    self.rigRolls[bone] = self.computeRoll(normal, bone)
                else:
                    self.rigRolls[bone] = roll
                
        else:
            self.joints += rig_joints.Joints #+ rig_joints.FloorJoints
            self.setupJoints()
            self.moveOriginToFloor()
            CArmature.setup(self)
        
        if self.config.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = proxy.getCoords()
                    (locations, boneList, weights) = exportutils.rig.readRigFile(proxy.rig, amt.mesh, coord=coord) 
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    appendRigBones(boneList, proxy.name, L_CLO, body, amt)
        

    def computeNormal(self, j1, j2, j3):
        p1 = m2b(self.locations[j1])
        p2 = m2b(self.locations[j2])
        p3 = m2b(self.locations[j3])
        pvec = getUnitVector(p2-p1)
        yvec = getUnitVector(p3-p2)
        if pvec is None or yvec is None:
            return None
        else:
            return getUnitVector(np.cross(yvec, pvec))
    

    def computeRoll(self, normal, bone):
        if normal is None:
            return 0

        p1 = m2b(self.rigHeads[bone])
        p2 = m2b(self.rigTails[bone])
        xvec = normal
        yvec = getUnitVector(p2-p1)
        xy = np.dot(xvec,yvec)
        #self.rigTails[bone] = b2m(p2-xy*xvec)
        yvec = getUnitVector(yvec-xy*xvec)
        zvec = getUnitVector(np.cross(xvec, yvec))
        if zvec is None:
            return 0
        else:
            mat = np.array((xvec,yvec,zvec))
            
        checkOrthogonal(mat)
        quat = tm.quaternion_from_matrix(mat)
        if abs(quat[0]) < 1e-4:
            roll = 0
        else:
            roll = math.pi - 2*math.atan(quat[2]/quat[0])
        if roll > math.pi:
            roll -= 2*math.pi
        print "  roll", bone, roll/D
        return roll
        
        
    def setupJoints (self):    
        """
        Evaluate symbolic expressions for joint locations and store them in self.locations.
        Joint locations are specified symbolically in the *Joints list in the beginning of the
        rig_*.py files (e.g. ArmJoints in rig_arm.py). 
        """
        
        scale = self.config.scale
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
                self.locations[key] = (self.mesh.coord[v] + offset)
            elif typ == 'vl':
                ((k1, v1), (k2, v2)) = data
                loc1 = self.mesh.coord[int(v1)]
                loc2 = self.mesh.coord[int(v2)]
                self.locations[key] = (k1*loc1 + k2*loc2)
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
            self.origin = self.locations['ground']
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


    def sortBones(self, bones):
        children = {}
        roots = []
        for bone in bones.keys():
            children[bone] = []
        for bone in bones.keys():
            (roll, parent, flags, layers) = bones[bone]
            if parent:
                children[parent].append(bone)
            elif self.master:
                if bone == self.master:
                    roots.append(bone)
                else:
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

   

       
