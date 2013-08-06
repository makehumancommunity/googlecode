#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Geometry export

"""

import numpy as np
from .dae_node import rotateLoc

#----------------------------------------------------------------------
#   library_geometry
#----------------------------------------------------------------------

def writeLibraryGeometry(fp, rmeshes, config):
    fp.write('\n  <library_geometries>\n')
    for rmesh in rmeshes:
        writeGeometry(fp, rmesh, config)
    fp.write('  </library_geometries>\n')


def writeGeometry(fp, rmesh, config):
    obj = rmesh.object
    nVerts = len(obj.coord)
    nUvVerts = len(obj.texco)
    nWeights = len(rmesh.skinWeights)
    nShapes = len(rmesh.shapes)

    fp.write('\n' +
        '    <geometry id="%sMesh" name="%s">\n' % (rmesh.name,rmesh.name) +
        '      <mesh>\n' +
        '        <source id="%s-Position">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-Position-array">\n' % (3*nVerts,rmesh.name) +
        '          ')


    for co in obj.coord:
        (x,y,z) = rotateLoc(co, config)
        fp.write("%.4f %.4f %.4f " % (x,y,z))

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-Position-array" stride="3">\n' % (nVerts,rmesh.name) +
        '              <param type="float" name="X"></param>\n' +
        '              <param type="float" name="Y"></param>\n' +
        '              <param type="float" name="Z"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')

    # Normals

    if config.useNormals:
        obj.calcFaceNormals()
        nNormals = len(obj.fnorm)
        fp.write(
            '        <source id="%s-Normals">\n' % rmesh.name +
            '          <float_array count="%d" id="%s-Normals-array">\n' % (3*nNormals,rmesh.name) +
            '          ')

        for no in obj.fnorm:
            (x,y,z) = rotateLoc(no, config)
            fp.write("%.4f %.4f %.4f " % (x,y,z))

        fp.write('\n' +
            '          </float_array>\n' +
            '          <technique_common>\n' +
            '            <accessor count="%d" source="#%s-Normals-array" stride="3">\n' % (nNormals,rmesh.name) +
            '              <param type="float" name="X"></param>\n' +
            '              <param type="float" name="Y"></param>\n' +
            '              <param type="float" name="Z"></param>\n' +
            '            </accessor>\n' +
            '          </technique_common>\n' +
            '        </source>\n')

    # UV coordinates

    fp.write(
        '        <source id="%s-UV">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-UV-array">\n' % (2*nUvVerts,rmesh.name) +
        '           ')


    for uv in obj.texco:
        fp.write(" %.4f %.4f" % tuple(uv))

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-UV-array" stride="2">\n' % (nUvVerts,rmesh.name) +
        '              <param type="float" name="S"></param>\n' +
        '              <param type="float" name="T"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')

    # Faces

    fp.write(
        '        <vertices id="%s-Vertex">\n' % rmesh.name +
        '          <input semantic="POSITION" source="#%s-Position"/>\n' % rmesh.name +
        '        </vertices>\n')

    checkFaces(rmesh, nVerts, nUvVerts)
    #writePolygons(fp, rmesh, config)
    writePolylist(fp, rmesh, config)

    fp.write(
        '      </mesh>\n' +
        '    </geometry>\n')

    for name,shape in rmesh.shapes:
        writeShapeKey(fp, name, shape, rmesh, config)
    return


def writeShapeKey(fp, name, shape, rmesh, config):
    obj = rmesh.object
    nVerts = len(obj.coord)

    # Verts

    fp.write(
        '    <geometry id="%sMeshMorph_%s" name="%s">\n' % (rmesh.name, name, name) +
        '      <mesh>\n' +
        '        <source id="%sMeshMorph_%s-positions">\n' % (rmesh.name, name) +
        '          <float_array id="%sMeshMorph_%s-positions-array" count="%d">\n' % (rmesh.name, name, 3*nVerts) +
        '           ')

    target = np.array(obj.coord)
    for n,dr in shape.items():
        target[n] += np.array(dr)
    for co in target:
        loc = rotateLoc(co, config)
        fp.write(" %.4g %.4g %.4g" % tuple(loc))

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sMeshMorph_%s-positions-array" count="%d" stride="3">\n' % (rmesh.name, name, nVerts) +
        '              <param name="X" type="float"/>\n' +
        '              <param name="Y" type="float"/>\n' +
        '              <param name="Z" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')

    # Normals
    """
    fp.write(
'        <source id="%sMeshMorph_%s-normals">\n' % (rmesh.name, name) +
'          <float_array id="%sMeshMorph_%s-normals-array" count="18">\n' % (rmesh.name, name))
-0.9438583 0 0.3303504 0 0.9438583 0.3303504 0.9438583 0 0.3303504 0 -0.9438583 0.3303504 0 0 -1 0 0 1
    fp.write(
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sMeshMorph_%s-normals-array" count="6" stride="3">\n' % (rmesh.name, name) +
        '              <param name="X" type="float"/>\n' +
        '              <param name="Y" type="float"/>\n' +
        '              <param name="Z" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    """

    # Polylist

    fp.write(
        '        <vertices id="%sMeshMorph_%s-vertices">\n' % (rmesh.name, name) +
        '          <input semantic="POSITION" source="#%sMeshMorph_%s-positions"/>\n' % (rmesh.name, name) +
        '        </vertices>\n' +
        '        <polylist count="%d">\n' % len(obj.fvert) +
        '          <input semantic="VERTEX" source="#%sMeshMorph_%s-vertices" offset="0"/>\n' % (rmesh.name, name) +
        #'          <input semantic="NORMAL" source="#%sMeshMorph_%s-normals" offset="1"/>\n' % (rmesh.name, name) +
        '          <vcount>')

    for fv in obj.fvert:
        if fv[0] == fv[3]:
            fp.write("3 ")
        else:
            fp.write("4 ")

    fp.write('\n' +
        '          </vcount>\n' +
        '          <p>')

    for fv in obj.fvert:
        if fv[0] == fv[3]:
            fp.write("%d %d %d " % (fv[0], fv[1], fv[2]))
        else:
            fp.write("%d %d %d %s " % (fv[0], fv[1], fv[2], fv[3]))

    fp.write('\n' +
        '          </p>\n' +
        '        </polylist>\n' +
        '      </mesh>\n' +
        '    </geometry>\n')


#
#   writePolygons(fp, rmesh, config):
#   writePolylist(fp, rmesh, config):
#

def writePolygons(fp, rmesh, config):
    obj = rmesh.object
    fp.write(
        '        <polygons count="%d">\n' % len(obj.fvert) +
        '          <input offset="0" semantic="VERTEX" source="#%s-Vertex"/>\n' % rmesh.name +
        '          <input offset="1" semantic="NORMAL" source="#%s-Normals"/>\n' % rmesh.name +
        '          <input offset="2" semantic="TEXCOORD" source="#%s-UV"/>\n' % rmesh.name)

    for fn,fverts in enumerate(obj.fvert):
        fuv = obj.fuvs[fn]
        fp.write('          <p>')
        for n,vn in enumerate(fverts):
            fp.write("%d %d %d " % (vn, vn, fuv[n]))
        fp.write('</p>\n')

    fp.write('\n' +
        '        </polygons>\n')
    return

def writePolylist(fp, rmesh, config):
    obj = rmesh.object
    fp.write(
        '        <polylist count="%d">\n' % len(obj.fvert) +
        '          <input offset="0" semantic="VERTEX" source="#%s-Vertex"/>\n' % rmesh.name)

    if config.useNormals:
        fp.write(
        '          <input offset="1" semantic="NORMAL" source="#%s-Normals"/>\n' % rmesh.name +
        '          <input offset="2" semantic="TEXCOORD" source="#%s-UV"/>\n' % rmesh.name +
        '          <vcount>')
    else:
        fp.write(
        '          <input offset="1" semantic="TEXCOORD" source="#%s-UV"/>\n' % rmesh.name +
        '          <vcount>')

    for fv in obj.fvert:
        if fv[0] == fv[3]:
            fp.write('3 ')
        else:
            fp.write('4 ')

    fp.write('\n' +
        '          </vcount>\n'
        '          <p>')

    for fn,fv in enumerate(obj.fvert):
        fuv = obj.fuvs[fn]
        if fv[0] == fv[3]:
            nverts = 3
        else:
            nverts = 4
        if config.useNormals:
            for n in range(nverts):
                fp.write("%d %d %d " % (fv[n], fn, fuv[n]))
        else:
            for n in range(nverts):
                fp.write("%d %d " % (fv[n], fuv[n]))

    fp.write(
        '          </p>\n' +
        '        </polylist>\n')
    return

#
#   checkFaces(rmesh, nVerts, nUvVerts):
#

def checkFaces(rmesh, nVerts, nUvVerts):
    obj = rmesh.object
    for fn,fverts in enumerate(obj.fvert):
        for n,vn in enumerate(fverts):
            uv = obj.fuvs[fn][n]
            if vn > nVerts:
                raise NameError("v %d > %d" % (vn, nVerts))
            if uv > nUvVerts:
                raise NameError("uv %d > %d" % (uv, nUvVerts))
    return
