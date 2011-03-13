#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Skeleton structure.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2011

**Licensing:**         GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
--------

This module implements a skeleton structure used in exporters and the skeleton visualizer.  

"""

from aljabr import vsub, vmul, centroid, vcross, vdot, vnorm, axisAngleToQuaternion
from math import acos

class Joint:

    """
  This class contains a simple constructor method for a data structure used to support 
  the BVH export functions. 
  A hierarchical nested list of these objects is defined to hold the joint positions and
  the relationship between joints. 
  """

    def __init__(self, name, children):
        self.name = name
        self.parent = None
        self.children = children
        self.position = [0.0, 0.0, 0.0]         # Global position in the scene
        self.offset = [0.0, 0.0, 0.0]           # Position Relative to the parent joint
        self.direction = [0.0, 0.0, 0.0, 0.0]   # Global rotation in the scene        
        # rpy values : xyz rotation
        self.rotation = [0.0, 0.0, 0.0]    # Rotation relative to the parent joint - axis of rotation is relative to parent
        # xyz limits
        self.limits = [[-180,180],[-180,180],[-180,180]]
        self.bindedVects = []
        self.index = 0
        self.radius = 0
        
        for child in children:
            child.parent = self

class Skeleton:
    
    def __init__(self):
        
        self.root = Joint('joint-pelvis', [Joint('joint-spine4', [Joint('joint-spine3', [Joint('joint-spine2', [Joint('joint-spine1', [Joint('joint-neck', [Joint('joint-head', [Joint('joint-mouth',
            []), Joint('joint-l-eye', []), Joint('joint-r-eye', [])])]), Joint('joint-r-clavicle', [Joint('joint-r-scapula', [Joint('joint-r-shoulder', [Joint('joint-r-elbow',
            [Joint('joint-r-hand', [Joint('joint-r-finger-1-1', [Joint('joint-r-finger-1-2', [Joint('joint-r-finger-1-3', [])])]), Joint('joint-r-finger-2-1',
            [Joint('joint-r-finger-2-2', [Joint('joint-r-finger-2-3', [])])]), Joint('joint-r-finger-3-1', [Joint('joint-r-finger-3-2',
            [Joint('joint-r-finger-3-3', [])])]), Joint('joint-r-finger-4-1', [Joint('joint-r-finger-4-2', [Joint('joint-r-finger-4-3', [])])]),
            Joint('joint-r-finger-5-1', [Joint('joint-r-finger-5-2', [Joint('joint-r-finger-5-3', [])])])])])])])]), 
            Joint('joint-l-clavicle', [Joint('joint-l-scapula',
            [Joint('joint-l-shoulder', [Joint('joint-l-elbow', [Joint('joint-l-hand', [Joint('joint-l-finger-1-1', [Joint('joint-l-finger-1-2',
            [Joint('joint-l-finger-1-3', [])])]), Joint('joint-l-finger-2-1', [Joint('joint-l-finger-2-2', [Joint('joint-l-finger-2-3', [])])]),
            Joint('joint-l-finger-3-1', [Joint('joint-l-finger-3-2', [Joint('joint-l-finger-3-3', [])])]), Joint('joint-l-finger-4-1',
            [Joint('joint-l-finger-4-2', [Joint('joint-l-finger-4-3', [])])]), Joint('joint-l-finger-5-1', [Joint('joint-l-finger-5-2',
            [Joint('joint-l-finger-5-3', [])])])])])])])])
            ])])]), 
            Joint('joint-r-upper-leg', [Joint('joint-r-knee', [Joint('joint-r-ankle',
            [Joint('joint-r-toe-1-1', [Joint('joint-r-toe-1-2', [])]), Joint('joint-r-toe-2-1', [Joint('joint-r-toe-2-2', [Joint('joint-r-toe-2-3', [])])]),
            Joint('joint-r-toe-3-1', [Joint('joint-r-toe-3-2', [Joint('joint-r-toe-3-3', [])])]), Joint('joint-r-toe-4-1', [Joint('joint-r-toe-4-2',
            [Joint('joint-r-toe-4-3', [])])]), Joint('joint-r-toe-5-1', [Joint('joint-r-toe-5-2', [Joint('joint-r-toe-5-3', [])])])])])]),
            Joint('joint-l-upper-leg', [Joint('joint-l-knee', [Joint('joint-l-ankle', [Joint('joint-l-toe-1-1', [Joint('joint-l-toe-1-2', [])]),
            Joint('joint-l-toe-2-1', [Joint('joint-l-toe-2-2', [Joint('joint-l-toe-2-3', [])])]), Joint('joint-l-toe-3-1', [Joint('joint-l-toe-3-2',
            [Joint('joint-l-toe-3-3', [])])]), Joint('joint-l-toe-4-1', [Joint('joint-l-toe-4-2', [Joint('joint-l-toe-4-3', [])])]), Joint('joint-l-toe-5-1',
            [Joint('joint-l-toe-5-2', [Joint('joint-l-toe-5-3', [])])])])])])])])
        
        #if (humanMesh):
        file = open("data/joint-bindings.txt")
        while (1): #don't you love it when infinite loops break the proggie
          line = file.readline()
          line = line.rstrip()
          #print "joint-"+line
          if not line: break 
          j = self.__getJoint(self.root, "joint-"+line)
          line = file.readline()
          line = line.split()
          for vert in line:
            j.bindedVects.append(int(vert))
        
        self.joints = 0
        self.endEffectors = 0
            
    def update(self, mesh):
        
        self.__calcJointOffsets(mesh, self.root)
        
    def getJoint(self, name):
        
        return self.__getJoint(self.root, name)
            
    def __getJoint(self, joint, name):
        
        if joint.name == name:
            return joint
            
        for child in joint.children:
            j = self.__getJoint(child, name)
            if j:
                return j
                
        return None

    def __calcJointOffsets(self, mesh, joint, parent=None):
        """
        This function calculates the position and offset for a joint and calls itself for 
        each 'child' joint in the hierarchical joint structure. 
        
        Parameters
        ----------
        
        mesh:     
          *Object3D*.  The object whose information is to be used for the calculation.
        joint:     
          *Joint Object*.  The joint object to be processed by this function call.
        parent:     
          *Joint Object*.  The parent joint object or 'None' if not specified.
        """

        # Calculate joint positions
        g = mesh.getFaceGroup(joint.name)
        verts = []
        for f in g.faces:
            for v in f.verts:
                verts.append(v.co)
        joint.position = centroid(verts)

        # Calculate offset
        if parent:
            joint.offset = vsub(joint.position, parent.position)
            
        # Calculate direction
        direction = vnorm(joint.offset)
        axis = vnorm(vcross([0.0, 0.0, 1.0], direction))
        angle = acos(vdot([0.0, 0.0, 1.0], direction))
        joint.direction = axisAngleToQuaternion(axis, angle)
        
        # Calculate rotation
        if parent:
            v1 = vmul(vnorm(parent.offset), -1.0)
            v2 = vnorm(joint.offset)
            axis = vnorm(vcross(v1, v2))
            angle = acos(vdot(v1, v2))
            joint.rotation = axisAngleToQuaternion(axis, angle)   
            
        # Update counters and set index
        joint.index = self.joints
        self.joints += 1
        if not joint.children:
            self.endEffectors += 1

        # Calculate child offsets
        for child in joint.children:
            self.__calcJointOffsets(mesh, child, joint)

