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

import os
import math
import numpy as np
import transformations as tm
from collections import OrderedDict
import mh2proxy
import exportutils

from .flags import *
from . import base_amt
from .base_amt import BaseArmature
from .utils import *

from . import rig_joints
from . import rig_bones
    
#-------------------------------------------------------------------------------        
#   Python Armature
#-------------------------------------------------------------------------------        

class PythonArmature(BaseArmature):

    def __init__(self, name, human, config):    
        BaseArmature. __init__(self, name, human, config)
        self.master = None
        self.reparents = {}

        self.useDeformBones = False
        self.useDeformNames = False
        self.useSplitBones = False
        self.splitBones = {}

        self.planes = rig_bones.Planes
        self.planeJoints = []
        self.vertexGroupFiles = []
        self.headName = 'Head'


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
        

    def addIkChains(self, boneInfo, bones, ikChains):
        for bone,data in boneInfo.items():
            (roll, parent, flags, layers) = data
            headTail = self.headsTails[bone]
            base,ext = splitBoneName(bone)
            parent = safeGet(self.reparents, bone, parent)
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
            parent = safeGet(self.reparents, bone, parent)
                
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

        self.vertexGroupFiles += ["leftright"]        
        vgroupList = []
        vgroups = {}
        for file in self.vertexGroupFiles:
            filepath = os.path.join("shared/armature/vertexgroups", file+".vgrp")
            readVertexGroups(filepath, vgroups, vgroupList)
        
        if self.useDeformNames:
            for bone,vgroup in vgroupList:
                base = splitBoneName(bone)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bone, vgroup)
                elif not self.useSplitBones:
                    defname = "DEF-"+bone
                    self.vertexWeights[defname] = vgroup
                else:
                    defname = "DEF-"+bone
                    try:
                        self.bones[defname]
                        self.vertexWeights[defname] = vgroup
                    except KeyError:
                        self.vertexWeights[bone] = vgroup
            
        elif self.useSplitBones:
            for bone,vgroup in vgroupList:
                base = splitBoneName(bone)[0]
                if base in self.splitBones.keys():
                    self.splitVertexGroup(bone, vgroup)
                else:
                    self.vertexWeights[bone] = vgroup
            
        else:
            for bone,vgroup in vgroupList:
                self.vertexWeights[bone] = vgroup



    def splitVertexGroup(self, bone, vgroup):
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
            self.vertexWeights[defname1] = vgroup1
            self.vertexWeights[defname2] = vgroup2
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
            self.vertexWeights[defname1] = vgroup1
            self.vertexWeights[defname2] = vgroup2
            self.vertexWeights[defname3] = vgroup3
        
    
    def getHeadTail(self, bone):
        return self.headsTails[bone]
        
    def setHeadTail(self, bone, head, tail):
        self.headsTails[bone] = (head,tail)


    def setup(self):
        if self.rigtype not in ["mhx", "basic", "rigify"]:
            print "NOT py", self.rigtype
            halt

        self.setupJoints()       
        self.setupNormals()
        self.setupPlaneJoints()
        self.moveOriginToFloor()
        self.createBones({})
        self.getVertexGroups()

        for bone in self.bones.keys():
            head,tail = self.headsTails[bone]
            self.heads[bone] = self.findLocation(head)
            self.tails[bone] = self.findLocation(tail)

        for bone in self.bones.keys():
            (roll, parent, flags, layers) = self.bones[bone]
            if isinstance(roll, str) and roll[0:5] == "Plane":
                normal = m2b(self.normals[roll])
                self.rolls[bone] = self.computeRoll(normal, bone)
            else:
                self.rolls[bone] = roll
                
        
        if self.config.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = proxy.getCoords()
                    self.fromRigFile(proxy.rig, amt.mesh, coord=coord) 
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    #appendRigBones(boneList, proxy.name, L_CLO, body, amt)
        

    def setupNormals(self):
        self.normals = {}
        for plane,joints in self.planes.items():
            j1,j2,j3 = joints
            p1 = self.locations[j1]
            p2 = self.locations[j2]
            p3 = self.locations[j3]
            pvec = getUnitVector(p2-p1)
            yvec = getUnitVector(p3-p2)
            if pvec is None or yvec is None:
                self.normals[plane] = None
            else:
                self.normals[plane] = getUnitVector(np.cross(yvec, pvec))
    

    def computeRoll(self, normal, bone):
        if normal is None:
            return 0

        p1 = m2b(self.heads[bone])
        p2 = m2b(self.tails[bone])
        xvec = normal
        yvec = getUnitVector(p2-p1)
        xy = np.dot(xvec,yvec)
        #self.tails[bone] = b2m(p2-xy*xvec)
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
    

    def setupPlaneJoints (self):    
        for key,data in self.planeJoints:
            p0,plane,dist = data
            x0 = self.locations[p0]            
            p1,p2,p3 = self.planes[plane]
            vec = self.locations[p3] - self.locations[p1]
            vec /= math.sqrt(np.dot(vec,vec))
            n = self.normals[plane]
            t = np.cross(n, vec)
            self.locations[key] = x0 + dist*t

    
    def moveOriginToFloor(self):
        if self.config.feetOnGround:
            self.origin = self.locations['ground']
            for key in self.locations.keys():
                self.locations[key] = self.locations[key] - self.origin
        else:
            self.origin = np.array([0,0,0], float)
        return
    
        
    def setupHeadsTails(self):
        self.heads = {}
        self.tails = {}
        scale = self.config.scale
        for (bone, head, tail) in self.headsTails:
            self.heads[bone] = findLocation(self, head)
            self.tails[bone] = findLocation(self, tail)
        
    
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
    
        


       
