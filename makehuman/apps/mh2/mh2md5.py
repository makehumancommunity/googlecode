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
from skeleton import Skeleton

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

    skeleton = Skeleton()
    skeleton.update(obj)

    f = open(filepath, 'w')
    f.write('MD5Version 10\n')
    f.write('commandline ""\n\n')
    f.write('numJoints %d\n' % (skeleton.joints+1)) # Amount of joints + the hardcoded origin below
    f.write('numMeshes %d\n\n' % (len(stuffs)))
    
    f.write('joints {\n')
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % ('origin', -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    writeJoint(f, skeleton.root)
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
        for fn,fverts in enumerate(obj.fvert):
            # tri [triIndex] [vertIndex1] [vertIndex2] [vertIndex3]
            f.write('\ttri %d %d %d %d\n' % (2*fn, fverts[2], fverts[1], fverts[0]))
            f.write('\ttri %d %d %d %d\n' % (2*fn+1, fverts[0], fverts[3], fverts[2]))

        f.write('\n\tnumweights %d\n' % (len(obj.coord)))
        for idx,co in enumerate(obj.coord):
            # TODO: We attach all vertices to the root with weight 1.0, this should become
            # real weights to the correct bones
            # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
            f.write('\tweight %d %d %f ( %f %f %f )\n' % (idx, 0, 1.0, co[0], -co[2], co[1]))
        f.write('}\n\n')
    f.close()
    

def writeJoint(f, joint):
    """
  This function writes out information describing one joint in MD5 format. 
  
  Parameters
  ----------
  
  f:     
    *file handle*.  The handle of the file being written to.
  joint:     
    *Joint object*.  The joint object to be processed by this function call.
  ident:     
    *integer*.  The joint identifier.
  """
    if joint.parent:
        parentIndex = joint.parent.index
    else:
        parentIndex = 0
    # "[boneName]"   [parentIndex] ( [xPos] [yPos] [zPos] ) ( [xOrient] [yOrient] [zOrient] )
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % (joint.name, parentIndex,
        joint.position[0], joint.position[1], joint.position[2],
        joint.direction[0], joint.direction[1], joint.direction[2]))

    for joint in joint.children:
        writeJoint(f, joint)
