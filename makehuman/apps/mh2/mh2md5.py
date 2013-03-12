#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Export to id Software's MD5 format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements a plugin to export MakeHuman mesh and skeleton data to id Software's MD5 format.
See http://www.modwiki.net/wiki/MD5MESH_(file_format) for information on the format.

Requires:

- base modules

"""

__docformat__ = 'restructuredtext'

import os
import numpy as np
import exportutils

def exportMd5(human, filepath, config):
    """
    This function exports MakeHuman mesh and skeleton data to id Software's MD5 format. 
    
    Parameters
    ----------
   
    human:     
      *Human*.  The object whose information is to be used for the export.
    filepath:     
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """

    obj = human.meshData
    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    stuffs = exportutils.collect.setupObjects(
        name, 
        human,
        config=config,
        helpers=config.helpers, 
        hidden=config.hidden, 
        eyebrows=config.eyebrows, 
        lashes=config.lashes,
        subdivide=config.subdivide)

    if human.skeleton:
        numJoints = human.skeleton.getBoneCount() +1 # Amount of joints + the hardcoded origin below
    else:
        numJoints = 1

    f = open(filepath, 'w')
    f.write('MD5Version 10\n')
    f.write('commandline ""\n\n')
    f.write('numJoints %d\n' % numJoints) 
    f.write('numMeshes %d\n\n' % (len(stuffs)))
    
    f.write('joints {\n')
    # Hardcoded root joint
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % ('origin', -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    if human.skeleton:
        for bone in human.skeleton.getBones():
            writeBone(f, bone)
    f.write('}\n\n')

    for stuff in stuffs:
        obj = stuff.meshInfo.object
        
        f.write('mesh {\n')
        if stuff.texture:
            texfolder,texname = stuff.texture
            f.write('\tshader "%s"\n' % (texname)) # TODO: create the shader file

        f.write('\n\tnumverts %d\n' % (len(obj.coord)))
        uvs = np.zeros(len(obj.coord), dtype=np.uint32)
        uvs[obj.fvert] = obj.fuvs

        for vert in xrange(len(obj.coord)):
            if obj.has_uv:
                u, v = obj.texco[uvs[vert]]
            else:
                u, v = 0, 0
            # vert [vertIndex] ( [texU] [texV] ) [weightIndex] [weightElem]
            f.write('\tvert %d ( %f %f ) %d %d\n' % (vert, u, 1.0-v, vert, 1))

        del uvs

        f.write('\n\tnumtris %d\n' % (len(obj.fvert) * 2))
        fn = 0
        for fv in obj.fvert:
            # tri [triIndex] [vertIndex1] [vertIndex2] [vertIndex3]
            f.write('\ttri %d %d %d %d\n' % (fn, fv[2], fv[1], fv[0]))
            fn += 1
            if fv[0] != fv[3]:
                f.write('\ttri %d %d %d %d\n' % (fn, fv[0], fv[3], fv[2]))
                fn += 1

        f.write('\n\tnumweights %d\n' % (len(obj.coord)))
        for idx,co in enumerate(obj.coord):
            # TODO: We attach all vertices to the root with weight 1.0, this should become
            # real weights to the correct bones
            # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
            f.write('\tweight %d %d %f ( %f %f %f )\n' % (idx, 0, 1.0, co[0], -co[2], co[1]))
        f.write('}\n\n')
    f.close()
    

def writeBone(f, bone):
    """
  This function writes out information describing one joint in MD5 format. 
  
  Parameters
  ----------
  
  f:     
    *file handle*.  The handle of the file being written to.
  joint:     
    *Bone object*.  The bone object to be processed by this function call.
  """
    if bone.parent:
        parentIndex = bone.parent.index + 1
    else:
        parentIndex = 0 # Refers to the hard-coded root joint
    # "[boneName]"   [parentIndex] ( [xPos] [yPos] [zPos] ) ( [xOrient] [yOrient] [zOrient] )
    headPos = bone.getRestHeadPos()
    direction = bone.getRestDirection()
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % (bone.name, parentIndex,
        headPos[0], headPos[1], headPos[2],
        direction[0], direction[1], direction[2]))
