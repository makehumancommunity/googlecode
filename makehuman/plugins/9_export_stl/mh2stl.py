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
    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    rmeshes,_amt = exportutils.collect.setupObjects(
        name,
        human,
        config=config,
        useHelpers=config.useHelpers,
        subdivide=config.subdivide)

    fp = open(filepath, 'w')
    solid = name.replace(' ','_')
    fp.write('solid %s\n' % solid)

    for rmesh in rmeshes:
        obj = rmesh.object
        fp.write("".join( [(
            'facet normal %f %f %f\n' % tuple(obj.fnorm[fn]) +
            '\touter loop\n' +
            '\t\tvertex %f %f %f\n' % tuple(obj.coord[fv[0]]) +
            '\t\tvertex %f %f %f\n' % tuple(obj.coord[fv[1]]) +
            '\t\tvertex %f %f %f\n' % tuple(obj.coord[fv[2]]) +
            '\tendloop\n' +
            '\tendfacet\n' +
            'facet normal %f %f %f\n' % tuple(obj.fnorm[fn]) +
            '\touter loop\n' +
            '\t\tvertex %f %f %f\n' % tuple(obj.coord[fv[2]]) +
            '\t\tvertex %f %f %f\n' % tuple(obj.coord[fv[3]]) +
            '\t\tvertex %f %f %f\n' % tuple(obj.coord[fv[0]]) +
            '\tendloop\n' +
            '\tendfacet\n'
            ) for fn,fv in enumerate(obj.fvert)] ))

    fp.write('endsolid %s\n' % solid)
    fp.close()


def exportStlBinary(human, filepath, config, exportJoints = False):
    """
    human:
      *Human*.  The object whose information is to be used for the export.
    filepath:
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """

    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    rmeshes,_amt = exportutils.collect.setupObjects(
        name,
        human,
        config=config,
        useHelpers=config.useHelpers,
        subdivide=config.subdivide)

    fp = open(filepath, 'wb')
    fp.write('\x00' * 80)
    fp.write(struct.pack('<I', 0))
    count = 0

    for rmesh in rmeshes:
        obj = rmesh.object
        for fn,fv in enumerate(obj.fvert):
            fno = obj.fnorm[fn]
            co = obj.coord[fv]

            fp.write(struct.pack('<fff', fno[0], fno[1], fno[2]))
            fp.write(struct.pack('<fff', co[0][0], co[0][1], co[0][2]))
            fp.write(struct.pack('<fff', co[1][0], co[1][1], co[1][2]))
            fp.write(struct.pack('<fff', co[2][0], co[2][1], co[2][2]))
            fp.write(struct.pack('<H', 0))
            count += 1

            fp.write(struct.pack('<fff', fno[0], fno[1], fno[2]))
            fp.write(struct.pack('<fff', co[2][0], co[2][1], co[2][2]))
            fp.write(struct.pack('<fff', co[3][0], co[3][1], co[3][2]))
            fp.write(struct.pack('<fff', co[0][0], co[0][1], co[0][2]))
            fp.write(struct.pack('<H', 0))
            count += 1
    fp.seek(80)
    fp.write(struct.pack('<I', count))


