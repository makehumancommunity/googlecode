#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Export to stereolithography format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements a plugin to export MakeHuman mesh to stereolithography format.
See http://en.wikipedia.org/wiki/STL_(file_format) for information on the format.

Requires:

- base modules

"""

__docformat__ = 'restructuredtext'

import os
import struct
import exportutils

def exportStlAscii(human, filepath, config, exportJoints = False):
    """
    This function exports MakeHuman mesh and skeleton data to stereolithography ascii format. 
    
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
    config.addObjects(human)
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

    f = open(filepath, 'w')
    solid = name.replace(' ','_')
    f.write('solid %s\n' % solid)

    for stuff in stuffs:
        obj = stuff.meshInfo.object
        
        for face in obj.faces:
            #if not exportJoints and 'joint' in face.group.name:
            #    continue
            f.write('facet normal %f %f %f\n' % (face.no[0], face.no[1], face.no[2]))
            f.write('\touter loop\n')
            f.write('\t\tvertex %f %f %f\n' % (face.verts[0].co[0], face.verts[0].co[1], face.verts[0].co[2]))
            f.write('\t\tvertex %f %f %f\n' % (face.verts[1].co[0], face.verts[1].co[1], face.verts[1].co[2]))
            f.write('\t\tvertex %f %f %f\n' % (face.verts[2].co[0], face.verts[2].co[1], face.verts[2].co[2]))
            f.write('\tendloop\n')
            f.write('\tendfacet\n')
            
            f.write('facet normal %f %f %f\n' % (face.no[0], face.no[1], face.no[2]))
            f.write('\touter loop\n')
            f.write('\t\tvertex %f %f %f\n' % (face.verts[2].co[0], face.verts[2].co[1], face.verts[2].co[2]))
            f.write('\t\tvertex %f %f %f\n' % (face.verts[3].co[0], face.verts[3].co[1], face.verts[3].co[2]))
            f.write('\t\tvertex %f %f %f\n' % (face.verts[0].co[0], face.verts[0].co[1], face.verts[0].co[2]))
            f.write('\tendloop\n')
            f.write('\tendfacet\n')
        
    f.write('endsolid %s\n' % solid)
    f.close()

    
def exportStlBinary(human, filename, config, exportJoints = False):
    """
    human:     
      *Human*.  The object whose information is to be used for the export.
    filepath:     
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """    

    obj = human.meshData
    config.addObjects(human)
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

    # TL: should loop over stuff (clothes etc) but only do nude human for now.

    f = open(filename, 'wb')
    f.write('\x00' * 80)
    f.write(struct.pack('<I', 0))
    count = 0
    for face in obj.faces:
        if not exportJoints and 'joint' in face.group.name:
            continue
        f.write(struct.pack('<fff', face.no[0], face.no[1], face.no[2]))
        f.write(struct.pack('<fff', face.verts[0].co[0], face.verts[0].co[1], face.verts[0].co[2]))
        f.write(struct.pack('<fff', face.verts[1].co[0], face.verts[1].co[1], face.verts[1].co[2]))
        f.write(struct.pack('<fff', face.verts[2].co[0], face.verts[2].co[1], face.verts[2].co[2]))
        f.write(struct.pack('<H', 0))
        count += 1
        
        f.write(struct.pack('<fff', face.no[0], face.no[1], face.no[2]))
        f.write(struct.pack('<fff', face.verts[2].co[0], face.verts[2].co[1], face.verts[2].co[2]))
        f.write(struct.pack('<fff', face.verts[3].co[0], face.verts[3].co[1], face.verts[3].co[2]))
        f.write(struct.pack('<fff', face.verts[0].co[0], face.verts[0].co[1], face.verts[0].co[2]))
        f.write(struct.pack('<H', 0))
        count += 1
    f.seek(80)
    f.write(struct.pack('<I', count))

    
