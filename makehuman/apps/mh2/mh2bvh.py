#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Export anatomical and pose data as Biovision motion capture data in BVH format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements a plugin to export MakeHuman skeleton data in Biovision BVH format.
The BioVision Hierarchy formmat (BVH) is widely supported as a means of exchanging anatomical 
and pose data with other applications used for animating human forms.  

Requires:

- base modules

"""

__docformat__ = 'restructuredtext'

import gui3d
import bvh
import transformations as tm

def exportSkeleton(filename, addEmptyAnimation=True):
    """
    This function exports joint information describing the structure of the 
    MakeHuman humanoid mesh object in Biovision BVH format. 
    
    Parameters
    ----------
   
    filename:     
      *string*.  The filename of the file to export the object to.
    """
    human = gui3d.app.selectedHuman
    if not human.getSkeleton():
        gui3d.app.prompt('Error', 'You did not select a skeleton from the library.', 'OK')
        return


    # Write bvh file
    skel = human.getSkeleton()
    root = skel.roots[0]  # we assume a skeleton with only one root

    f = open(filename, 'w')
    f.write('HIERARCHY\n')
    f.write('ROOT ' + root.name + '\n')
    f.write('{\n')
    position = root.getRestHeadPos()
    f.write("\tOFFSET	%f  %f  %f\n" %(position[0],position[1],position[2]))
    f.write('\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n')
    for bone in root.children:
        writeBone(f, bone, 1)
    f.write('}\n')

    if addEmptyAnimation:
        f.write('MOTION\n')
        f.write('Frames:    1\n')
        f.write('Frame Time: 0.0\n')
        position = root.getRestHeadPos()
        f.write("%f  %f  %f" %(position[0],position[1],position[2]) )
        for i in xrange(len(skel.getJointNames())):
            f.write(" %f %f %f" %(0.0, 0.0, 0.0))
        f.write("\n")
    f.close()

def writeBone(f, bone, ident):
    """
  This function writes out information describing one joint in BVH format. 
  
  Parameters
  ----------
  
  f:     
    *file handle*.  The handle of the file being written to.
  bone:     
    *Bone object*.  The bone object to be processed by this function call.
  ident:     
    *integer*.  The joint identifier.
  """

    f.write('\t' * ident + 'JOINT ' + bone.name + '\n')
    f.write('\t' * ident + '{\n')
    offset = bone.getRestOffset()
    f.write('\t' * (ident + 1) + "OFFSET	%f  %f  %f\n" % (offset[0], offset[1], offset[2]))
    f.write('\t' * (ident + 1) + 'CHANNELS 3 Zrotation Xrotation Yrotation\n')
    if len(bone.children) > 0:
        for childBone in bone.children:
            writeBone(f, childBone, ident + 1)
    else:
        offset = bone.getRestTailPos() - bone.getRestHeadPos()
        f.write('\t' * (ident + 1) + 'End Site\n')
        f.write('\t' * (ident + 1) + '{\n')
        f.write('\t' * (ident + 2) + "OFFSET	%s	%s	%s\n" % (offset[0], offset[1], offset[2]))
        f.write('\t' * (ident + 1) + '}\n')
    f.write('\t' * ident + '}\n')

def exportAnimation(filename, animationName):
    human = gui3d.app.selectedHuman
    skel = human.getSkeleton()
    animationTrack = human.animated.getAnimation(animationName)
    D = bvh.D

    f = open(filename, 'a')
    f.write('MOTION\n')
    f.write('Frames: %s\n' % animationTrack.nFrames)
    f.write('Frame Time: %f\n' % (1.0/animationTrack.frameRate))
    joints = skel.getJointNames()
    jointToBoneIdx = {}
    for joint in joints:
        jointToBoneIdx[joint] = skel.getBone(joint).index

    for fIdx in xrange(animationTrack.nFrames):
        offset = fIdx * animationTrack.nBones
        for jIdx,joint in enumerate(joints):
            bIdx = jointToBoneIdx[joint]
            poseMat = animationTrack.data[offset + bIdx]
            if jIdx == 0:
                tx, ty, tz = poseMat[:3,3]
                f.write('%f %f %f ' % (tx, ty, tz))
            ay,ax,az = tm.euler_from_matrix(poseMat, "syxz")
            f.write('%f %f %f ' % (az/D, ax/D, ay/D))
        f.write('\n')
    f.close()
