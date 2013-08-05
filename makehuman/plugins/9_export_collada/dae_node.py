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

Node export

"""


def writeNode(fp, pad, rmesh, amt, config):

    fp.write('\n' +
        '%s<node id="%sObject" name="%s">\n' % (pad, rmesh.name,rmesh.name) +
        '%s  <matrix sid="transform">\n' % pad +
        '%s    1 0 0 0\n' % pad +
        '%s    0 1 0 0\n' % pad +
        '%s    0 0 1 0\n' % pad +
        '%s    0 0 0 1\n' % pad +
        '%s  </matrix>\n' % pad +
        '%s  <instance_controller url="#%s-skin">\n' % (pad, rmesh.name) +
        '%s    <skeleton>#%sSkeleton</skeleton>\n' % (pad, amt.roots[0].name))

    mat = rmesh.material
    matname = mat.name.replace(" ", "_")
    fp.write(
        '%s    <bind_material>\n' % pad +
        '%s      <technique_common>\n' % pad +
        '%s        <instance_material symbol="%s" target="#%s">\n' % (pad, matname, matname) +
        '%s          <bind_vertex_input semantic="UVTex" input_semantic="TEXCOORD" input_set="0"/>\n' % pad +
        '%s        </instance_material>\n' % pad +
        '%s      </technique_common>\n' % pad +
        '%s    </bind_material>\n' % pad)

    fp.write(
        '%s  </instance_controller>\n' % pad +
        '%s</node>\n' % pad)
    return


def rotateLoc(loc, config):
    return loc
    (x,y,z) = loc
    if config.rotate90X:
        yy = -z
        z = y
        y = yy
    if config.rotate90Z:
        yy = x
        x = -y
        y = yy
    return (x,y,z)


def writeBone(fp, hier, orig, extra, pad, amt, config):
    (bone, children) = hier
    if bone:
        nameStr = 'sid="%s"' % bone.name
        idStr = 'id="%s" name="%s"' % (bone.name, bone.name)
    else:
        nameStr = ''
        idStr = ''

    fp.write(
        '%s      <node %s %s type="JOINT" %s>\n' % (pad, extra, nameStr, idStr) +
        '%s        <matrix sid="transform">\n' % pad)
    mat = bone.matrixRelative
    for i in range(4):
        fp.write('%s          %.5f %.5f %.5f %.5f\n' % (pad, mat[i][0], mat[i][1], mat[i][2], mat[i][3]))
    fp.write('%s        </matrix>\n' % pad)

    for child in children:
        writeBone(fp, child, bone.head, '', pad+'  ', amt, config)

    fp.write('%s      </node>\n' % pad)
    return


