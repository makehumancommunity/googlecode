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

Base armature
"""

import os
import math
import gui3d
import mh2proxy
import log
from collections import OrderedDict

import numpy as np

from .flags import *

#-------------------------------------------------------------------------------        
#   Armature base class.
#-------------------------------------------------------------------------------        
       
class BaseArmature:

    def __init__(self, name, human, config):
        self.name = name
        self.human = human
        self.mesh = human.meshData
        self.boneLayers = "00000001"
        self.config = config
        self.rigtype = config.rigtype
        self.addConnectingBones = config.addConnectingBones
        self.root = None
        self.master = None
        self.proxies = {}
        self.roots = []
        self.bones = OrderedDict()
        self.hierarchy = []

        self.locations = {}
        self.heads = {}
        self.tails = {}
        self.rolls = {}
        self.parents = {}
        self.layers = {}
        self.flags = {}
        #self.weights = {}
        self.origin = [0,0,0]
        self.loadedShapes = {}
        
        self.boneList = []
        self.vertexWeights = OrderedDict([])
        self.joints = []
        self.headsTails = []
        self.boneDefs = []
        self.constraints = {}
        self.rotationLimits = {}
                

    def __repr__(self):
        return ("  <BaseArmature %s %s>" % (self.name, self.rigtype))
        

    def prefixWeights(self, weights, prefix):
        pweights = {}
        for name in weights.keys():
            if name in self.heads:
                pweights[name] = weights[name]
            else:
                pweights[prefix+name] = weights[name]
        return pweights


    def sortBones(self, bones):
        print "Sort", bones
        if self.addConnectingBones:            
            extras = []
            for bone in bones.keys():
                (roll, parent, flags, layers) = bones[bone]
                if parent:
                    head,_ = self.getHeadTail(bone)
                    _,ptail = self.getHeadTail(parent)
                    if head != ptail:
                        connector = bone+".conn"
                        extras.append((connector, (0, parent, F_CON, L_HELP)))
                        bones[bone] = (roll, connector, flags|F_CON, layers)
                        self.setHeadTail(connector, ptail, head)
                        
            for bone,data in extras:
                bones[bone] = data
            
        children = {}
        for bone in bones.keys():
            children[bone] = []

        for bone in bones.keys():
            (roll, parent, flags, layers) = bones[bone]
            if parent:
                children[parent].append(bone)
            elif self.master:
                if bone == self.master:
                    self.roots.append(bone)
                else:
                    bones[bone] = (roll, self.master, flags, layers)
                    children[self.master].append(bone)
            else:
                self.roots.append(bone)

        for root in self.roots:            
            self.sortBones1(root, self.hierarchy, bones, children)


    def sortBones1(self, bone, hier, bones, children):
        self.bones[bone] = bones[bone]
        subhier = []
        hier.append([bone, subhier])
        for child in children[bone]:
            self.sortBones1(child, subhier, bones, children)
        

    
